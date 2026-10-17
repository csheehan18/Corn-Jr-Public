"""What a server instance *is*, in one dataclass, on `voice/config.py`'s terms.

**Three sources, and the precedence is fixed: defaults, then a JSON file, then
the command line.** The person hosting a Corn-Jr configures him once -- which
checkpoint, whose packs, which tools may run -- and then talks to him; the file
is where that configuration lives, and a flag is how you try something without
editing it. `harness/voice/config.py` argued this order first and nothing here
improves on the argument.

**Unknown keys in the file are refused rather than ignored.** A misspelt
`packs` that silently did nothing would present as "he doesn't know my things",
which is the failure mode that costs an evening.

The file is `server.json` at the repo root by default, beside `overlay.json`
and `voice.json` -- per-machine state, not part of the artefact. Absent on a
fresh clone, and that is a working configuration.

**Booleans are stored in the positive.** The command line keeps the historical
`--no-grammar` / `--no-decline` / `--no-fold` / `--no-confirm` / `--no-log`
spellings -- a card that says it was read under `--no-decline` must stay
readable -- but a file key named `no_decline: false` is a double negative
nobody parses twice the same way. The flag and the field disagree in name and
agree in meaning, and `add_arguments` is the one place that mapping lives.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from .protocol import DEFAULT_HOST, DEFAULT_PORT

# Next to the repo, not next to this module -- it describes a machine, not the
# package. `.gitignore` carries it beside `overlay.json`.
DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "server.json"

# `corn.sample.DTYPES`'s keys, restated so that reading a config never imports
# torch -- the studio loads this module at startup to learn host and port, and
# paying a torch import for two strings would make its launch feel like the
# model load it exists to supervise. `scripts/check_serverconfig.py` asserts
# this tuple equals `sorted(corn.sample.DTYPES)`, so a drift is loud.
DTYPE_NAMES = ("bf16", "fp32")

# `corn.agent.DEFAULT_NOTES` / `corn.persona.DEFAULT_STATE` /
# `harness.sessionlog.DEFAULT_LOG`, restated as strings for the same
# torch-free reason, under the same guard.
DEFAULT_NOTES_STR = "notes.jsonl"
DEFAULT_PERSONA_STATE_STR = "persona_state.json"
DEFAULT_BIRTHDAY_LEAD = 3   # corn.persona.DEFAULT_BIRTHDAY_LEAD, same guard

# Keys a `server.json` may still carry from before a setting was removed, each
# with why. `load` drops them with a printed note; anything else unknown is
# still an error.
RETIRED = {
    "book": "calls and texts reach only you now (PLAN-PEOPLE section 7, "
            "2026-10-13); the people you keep belong in a pack table -- "
            "python scripts/contacts_to_people.py converts the old book",
}
DEFAULT_LOG_STR = str(Path("Saved Sessions") / "turns.jsonl")


class ConfigError(ValueError):
    """A configuration that cannot be run, said once and plainly."""


# One text per knob, used by both the flag and the studio's form tooltip --
# the `protocol.py` rule that a thing described twice will eventually be two
# things. Longer rationale stays on the modules these point at.
HELP = {
    "ckpt": "the checkpoint to serve",
    "host": "127.0.0.1 by default. A LAN bind is a decision: this server has "
            "no authentication and executes tools.",
    "port": "the TCP port clients connect to",
    "device": "cuda or cpu; cpu is untested per docs/RELEASE.md",
    "dtype": "weights precision. bf16 halves the footprint and is a different "
             "measurement condition rather than a free win -- greedy decoding "
             "turns a swapped logit into a different sentence. Reported in "
             "`info`",
    "temperature": "sampling for tool calls. 0.0 is greedy, which is what a "
                   "structured object with one right answer wants",
    "speech_temperature": "sampling for the social replies he writes himself. "
                          "Separate because greedy speech is the same "
                          "sentence forever; see corn/agent.py",
    "notes": "where save_note appends",
    "birthday_lead": "days ahead he mentions a birthday from the people store "
                     "(a pack table with a Birthday column), once per birthday. "
                     "The owner's three, 2026-10-13 (PLAN-PEOPLE section 9)",
    "persona_state": "where 'he already mentioned it today' is written, so a "
                     "restart on his birthday does not announce it twice. "
                     "Only read when packs supplied a persona",
    "doc": "a .txt or .md file to answer lookups from: while loaded, "
           "web_search reads the document first and the answer never leaves "
           "the machine. Load, replace or unload mid-session with the "
           "client's /doc",
    "packs": "a folder of the owner's own data: CSV/TSV files become "
             "exact-lookup tables, .txt/.md become prose the reader can "
             "extract from. Answers before the web is asked, entirely "
             "locally -- see harness/backends/packs.py",
    "search": "answer web_search from the internet instead of the corpus "
              "table. Opt-in because it sends the query to a third party -- "
              "see harness/backends/search.py",
    "extract": "read the whole passage a search returned rather than its "
               "lead sentence. Only bites with search on",
    "extract_gate": "score each window once before reading it, and let that "
                    "decide speak-or-decline instead of the generator -- "
                    "see corn/gate.py. Windows below --gate-threshold are "
                    "not read at all and the runtime declines for them; the "
                    "ones that are read cannot open with a decline. ON by "
                    "default since it was measured over whole passages "
                    "(+108 of 1,003, p < 1e-4); --no-extract-gate is the "
                    "control. Only bites with --extract",
    "gate_threshold": "where corn/gate.py's willingness stops meaning speak "
                      "(default -0.136, cross-validated over 1,003 whole "
                      "passages: joint 509 against an ungated null's 464, "
                      "p = 0.0003). LOWER makes him speak more, trading "
                      "correct abstentions for attempts",
    "reader": "who reads a window: `generate` decodes an answer and lets the "
              "gate decide whether to, `head` points at the span with "
              "corn/reader.py's boundary head and lets that head's verifier "
              "decide -- no decode at all, and the gate is bypassed because "
              "the verifier is the gate. `head` reads 389 of 721 answerable "
              "passages right at 200 of 282 correct silences against "
              "`generate`'s 282 and 227 (finding 87). `head_whole` reads the "
              "passage in one forward through an adapted trunk and reads 523 "
              "of 721 right at 198 correct silences (finding 116); it needs "
              "--reader-adapter and the trunk that adapter was fitted to. "
              "Only bites with --extract",
    "reader_adapter": "the whole-passage arm's checkpoint -- the rank-32 "
                      "adapter and the head that was fitted beside it, in one "
                      "file. It names the trunk it belongs to by sha256 and "
                      "the runtime refuses to load it onto another. Only "
                      "bites with --reader head_whole",
    "reader_whole_threshold": "where the whole-passage head's margin stops "
                              "meaning speak (default -1.174, the mean of two "
                              "cross-validated folds over 1,003 whole "
                              "passages under the bar protocol). LOWER makes "
                              "him speak more. NOT the same quantity as "
                              "--reader-threshold: that one is a verifier's "
                              "logit and this one is max s - s_null. Only "
                              "bites with --reader head_whole",
    "reader_threshold": "where corn/reader.py's verifier stops meaning speak "
                        "(default -2.02, the mean of two cross-validated "
                        "folds over 1,003 whole passages under the bar "
                        "protocol). LOWER makes him speak more. Only bites "
                        "with --reader head",
    "reader_extent_d": "how far below the best pair's score a longer span may "
                       "sit and still be spoken (default 2.0, up to three "
                       "candidate rows either side). 0 turns the extent rule "
                       "off; it is worth 6-8 passages of 721 at nothing lost. "
                       "Only bites with --reader head",
    "multi": "carry the transcript across turns. ON by default since "
             "2026-09-06 -- decision 6, the owner's, taken on arm 8's "
             "reissue column and its re-read under the seed: the class "
             "corn/agent.py's banner says is missing (a second <|user|> "
             "that does not call) is what arms 7 and 8 trained, and "
             "harness/historygrid.py reads reissued_query 0/36 and "
             "reissued_utterance 0/72 at depth 1 and depth 3 alike, "
             "copied_from `none` on all 72. --no-multi is the control "
             "every card measured before that date was read under",
    "seed_turn": "an utterance the runtime runs itself at start and at every "
                 "reset so the history is never empty. ON by default with "
                 "'what day is it', a hatched turn that costs no decode: the "
                 "misroute grid (STATUS 2026-09-05) read every tool family "
                 "routing 3-5x better with any tool turn in the history than "
                 "on an empty one, and the seed reproduces that column to the "
                 "cell. Works with or without --multi. --seed-turn '' turns "
                 "it off, which is the measurement control for the first-turn "
                 "number",
    "seed_trim": "how much of the seed turn's own text stays in the context: "
                 "`off` is the shipped runtime, `obs` drops its observation, "
                 "`both` drops its observation and its say, leaving the user "
                 "line and the call. The seed helps by its *shape* -- a call "
                 "in the history is what makes a first turn look like the "
                 "second turn the corpus taught -- and hurts by its "
                 "*content*: web_search.query is not a copy slot, so the "
                 "seed's own words can walk into a generated query. Measured "
                 "2026-09-06 over ten pack questions: seeded 7/10 on the "
                 "first turn against 10/10 unseeded, and 7/10 either way on "
                 "the second. An arm, not a setting, until a card says "
                 "otherwise",
    "seed_repass": "what to do about a `web_search` query the seed turn "
                   "wrote into: `contaminated` (default since 2026-09-07, "
                   "4k) decodes the call a second time with the seed taken "
                   "out of the context only when the query carries a content "
                   "word nobody said this conversation -- `today` and `what "
                   "day is it` out of the seed, `mew2` out of nowhere -- "
                   "keeps the second call only if it routes to the same tool, "
                   "and if the query is still contaminated after that sends "
                   "the utterance itself. A clean query costs nothing. "
                   "`always` is 4j as measured: every routed search call "
                   "decoded twice, 8/10 pack answers at position 1 against "
                   "7/10 off. `off` is the control every card before that "
                   "date was read under. The seed decides which tool and "
                   "never what argument, under every mode but off",
    "grammar": "--no-grammar turns off the call constraint. A measurement "
               "control, not a setting",
    "decline": "--no-decline withholds `decline` from the declared set and "
               "from the grammar's narrowing. A measurement, not a setting; "
               "see corn.agent.declaration_names",
    "fold": "--no-fold hands the model the utterance exactly as typed. ON by "
            "default -- the flag is the control a fold-dated card is read "
            "against. See corn.agent.fold_turn",
    "history_fold": "an evicted turn keeps its <|user|> and <|say|> and loses "
                    "its <|call|> and <|obs|>, instead of dropping whole -- 23 "
                    "tokens against 87, and the kept form is the chat_day "
                    "shape. ON by default since 2026-09-07 (decision 11): with "
                    "--budget 120 it holds four prior tool turns every time "
                    "where the shipped pair held one, and historygrid depth 3 "
                    "reads 8/8 routed with nothing reissued. --no-fold-history "
                    "is the control every card before that date was read "
                    "under; --multi only. See corn.agent.fold_entry and "
                    "docs/PLAN-CONVERSATION.md 4g and (tenth)",
    "confirm": "--no-confirm lets gated tools run without asking. They "
               "cannot be taken back; see harness/backends/confirm.py",
    "restrict": "answer social turns from the runtime pools only. A control, "
                "not a setting -- see corn/agent.py's social_rejection",
    "name_header": "put `name: <persona name>` as the first line of every "
                   "context, above the day and the declaration -- the line "
                   "arm 9's header design trains him to copy his name from "
                   "(PLAN-PERSONALITY (sixth)). Off by default: a checkpoint "
                   "that never saw the line gets the context it was measured on",
    "identity_check": "the identity hatch (who are you, are you an AI, a "
                      "question about his life): `on` answers from the pools "
                      "as it always has, `log` lets the turn route so the "
                      "weights answer and records the pool line the hatch "
                      "would have said as `identity_pool` on the say. "
                      "PLAN-PERSONALITY §7: the ledger reads arm 9 under log",
    "family_check": "hold his own social reply to the family the hatch "
                    "matched: `on` refuses a wrong-family reply everywhere "
                    "and a markerless one on farewell and consolation, "
                    "`log` serves every reply and reports what would have "
                    "been refused as soft_reject, `off` is the runtime before "
                    "2026-09-05. See corn/socialfam.py and "
                    "docs/PLAN-CONVERSATION.md 4a",
    "round_reserve": "tokens held back from the --multi history fit so a "
                     "turn's second round is not tail-cut at the head; "
                     "corn.agent.ROUND_ADDITION (114) is the measured maximum "
                     "a round appends. 0 is the shipped trimmer and the A/B's "
                     "control. See docs/PLAN-CONVERSATION.md 4h",
    "budget": "the generation reserve per round, in tokens (default 120 "
              "since 2026-09-07, decision 11; 200 before). Under --multi it "
              "is also what the history is fitted against, so a smaller "
              "reserve is a deeper conversation, and corn.agent's own "
              "maximum round is 60 tokens so nothing is cut at 120. With "
              "--fold-history the pair holds four prior tool turns where 200 "
              "held one. --budget 200 is the control. See "
              "docs/PLAN-CONVERSATION.md 4f and (tenth)",
    "buckets": "one decode graph per 128-slot window instead of always "
               "attending the full block. Default since 2026-09-07. Exact "
               "greedy parity on the shipped checkpoint at fp32 "
               "(scripts/check_decode.py, 96/96), so unlike --dtype this "
               "costs nothing in comparability: a card taken under it is "
               "still comparable with every fp32 row already published. "
               "--no-buckets is the control.",
    "compile_step": "Inductor-fuse the decode step before capture. Default "
                    "since 2026-09-07. Exact greedy parity on the shipped "
                    "checkpoint at fp32 (scripts/check_decode.py, 96/96). "
                    "The first step compiled pays Inductor once, which a "
                    "resident server absorbs and a per-turn process would "
                    "pay every turn. --no-compile is the control.",
    "prefix_reuse": "keep the KV of the prefix each round shares with the "
                    "last, instead of recomputing it (corn/decode.py "
                    "prefill(reuse=True), measured at 42.1%% of a turn's "
                    "prefill on single-call turns). Exact rather than "
                    "approximate -- `wpe` is what makes that true -- so rows "
                    "should not move and a card that moves them is the "
                    "finding. Off is the shipped path and every card's "
                    "control.",
    "log": "where structured turns are appended, one JSON line each",
    "logging": "--no-log keeps no structured record of this sitting. The "
               "prose transcript /saved writes is unaffected.",
    "tools": "the tools he is offered, comma-separated; empty means all of "
             "them. Narrows the declaration and the grammar together. Under "
             "--no-grammar a disabled tool the model emits anyway still "
             "executes, which is one more reason --no-grammar is a "
             "measurement control. `decline` is not a member -- it has its "
             "own flag",
    "tools_dir": "a folder of tool declaration files (JSON), each backed by "
                 "a command -- see harness/backends/toolsd.py. Empty means "
                 "off",
}


def _csv(text: str) -> list[str]:
    """`--tools a,b,c` -> ["a", "b", "c"]; bare commas and spaces forgiven."""
    return [t.strip() for t in text.split(",") if t.strip()]


@dataclass
class ServerConfig:
    """What the instance is wired to. Every field is a flag and a JSON key."""

    # -- what the instance is ------------------------------------------------
    ckpt: str = "checkpoints/nano20m_v1/ckpt.pt"
    packs: str = ""           # "" = no pack folder
    doc: str = ""             # "" = no document at start
    notes: str = DEFAULT_NOTES_STR
    persona_state: str = DEFAULT_PERSONA_STATE_STR
    birthday_lead: int = DEFAULT_BIRTHDAY_LEAD
    search: bool = False
    extract: bool = False
    # **On, and the argument for it changed twice before it settled.** It
    # went in off (Stage 1, single-window evidence only), then on when
    # `scripts/probe_multiwindow.py` read 1,003 whole passages -- but that
    # +108 was mostly the gated path not running `property_local` (+82), and
    # the gate's own share was significant only on the 400 items its
    # threshold had been swept on. `scripts/probe_gate_crossfit.py` found the
    # cause: the threshold, not the gate. Cross-validated on the runtime's
    # own population it is -0.136, and there the gated path reads joint 509
    # against an ungated, unvetoed null's 464 -- **+45 at p = 0.0003**, with
    # right answers *up* (282 against 279) and 95 fewer wrong ones.
    # `--no-extract-gate` is the control -- and note it produces flag-off
    # *with* the veto, which is the worst of the four arms measured.
    extract_gate: bool = True
    # **On since 2026-09-06 -- decision 6, the owner's, and the flag whose
    # default waited longest.** `corn/agent.py`'s banner is why it was off: a
    # second `<|user|>` meant "emit a call" in 1,720 transcripts of five
    # billion tokens and `<|say|>` in none of them, so carrying a transcript
    # across turns put him in a context the corpus only ever resolved one way.
    # Arms 7 and 8 trained that class (`--turns 2`, `--depth 2`), and the
    # column the decision was gated on is the one a second turn can spoil:
    # `harness/historygrid.py` reads `reissued_query` 0/36 and
    # `reissued_utterance` 0/72 on the shipped trunk at depth 1 *and* depth 3,
    # with `copied_from` `none` on all 72 -- finding 123's reading, re-read
    # 2026-09-06 under the seed turn, which had moved every history row one
    # depth deeper than it was measured at. `--no-multi` is the control, and
    # it is what every card written before that date was read under.
    multi: bool = True
    seed_turn: str = "what day is it"   # "" = no seed; see HELP
    seed_trim: str = "off"              # off | obs | both; see HELP
    # **`contaminated` since 2026-09-07 -- 4k, the gated form of 4j.** 4j
    # decoded every routed search call twice and was killed on its own bar
    # (8/10 against 9/10, PLAN-CONVERSATION 4j read). What it fixed it fixed
    # exactly: the argument channel. What 4k changes is *when*: the second
    # decode runs only on a query that carries a content word the person
    # never said this conversation -- `today` and `what day is it` out of
    # the seed, `mew2` out of nowhere -- and a query that is still
    # contaminated afterwards is replaced by the utterance itself, which is
    # the span he would have copied. A clean query costs nothing. `off` is
    # the control every card before that date was read under; `always` is
    # 4j as measured.
    seed_repass: str = "contaminated"   # off | always | contaminated; see HELP
    tools: list[str] = field(default_factory=list)   # [] = all declared
    tools_dir: str = ""       # "" = no declaration files

    # -- the machine ---------------------------------------------------------
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    device: str = "cuda"
    dtype: str = "fp32"

    # -- sampling ------------------------------------------------------------
    temperature: float = 0.0
    speech_temperature: float = 0.3
    # The literal rather than an import of `corn.gate.GATE_THRESHOLD`: this
    # module is the one the studio reads to draw a form, and pulling torch in
    # through `corn/` to learn a float would make a config page pay for a
    # framework. The two are held equal by `scripts/check_extract.py`, which
    # is the same "two descriptions must agree" guard the tools list gets.
    # Moved from -0.082 on 2026-09-01: that value was cross-validated on
    # single-window eval items and the runtime reads whole passages -- see
    # `corn/gate.py`.
    gate_threshold: float = -0.136

    # -- the reader ----------------------------------------------------------
    # **`head_whole` is the default since 2026-09-05 -- decision 7, the
    # owner's, taken on finding 124's numbers.** On Population A through the
    # real `read_passage` the whole-passage adapter reads 517 right at 197
    # correct silences against the generate-path gate's 230 at 256, at 23 ms
    # a passage; `--reader generate` and `--reader head` remain the arms, so
    # the comparison stays paired and internal. The adapter below is keyed to
    # the trunk `server.json` names and refuses any other.
    reader: str = "head_whole"
    # The literals rather than an import of `corn.reader`'s constants, for
    # `gate_threshold`'s reason: this module is what the studio reads to draw
    # a form and pulling torch in through `corn/` to learn two floats would
    # make a config page pay for a framework. `scripts/check_extract.py` holds
    # all three pairs equal.
    reader_threshold: float = -2.02
    reader_extent_d: float = 2.0
    # The whole-passage arm (finding 112, finding 116). Off with the rest of
    # the reader by default, and the same shipping decision has not been taken
    # for it either -- it reads +131 right answers over `head` on Population A
    # and one fewer correct silence, and the flag is what keeps that a paired
    # internal comparison. The path is here rather than in `corn/` for
    # `SPAN_HEAD`'s reason: a path on this disk is what the process happens to
    # be wired to.
    # Re-fit on the social8 trunk 2026-09-05 (finding 124); the ft4g pair was
    # `reader_whole_causal_s1.pt` at -1.174, and `load_adapter` refuses either
    # file on the other's trunk.
    reader_adapter: str = "checkpoints/reader_whole_social8_s1.pt"
    reader_whole_threshold: float = -1.280

    # -- measurement controls and the sitting's record -----------------------
    grammar: bool = True
    decline: bool = True
    fold: bool = True
    # **On since 2026-09-07 -- decision 11, the owner's, with `budget` 120
    # below.** Priced together on the real trimmer (PLAN-CONVERSATION,
    # tenth): the shipped pair held one prior tool turn whole and a second
    # 31% of the time; this pair holds four every time and a sixth 80% of
    # the time, six chat turns either way. Live under the pair: historygrid
    # depth 3 routes 8/8 on every arm with nothing reissued, converse and
    # chaingrid unmoved. `--no-fold-history` and `--budget 200` are the
    # controls every card before that date was read under.
    history_fold: bool = True
    confirm: bool = True
    restrict: bool = False
    family_check: str = "on"
    identity_check: str = "on"
    name_header: bool = False
    round_reserve: int = 0
    budget: int = 120           # decision 11; see history_fold above
    # **Both are exact, which is the whole reason they can be defaults.**
    # `scripts/check_decode.py --ckpt checkpoints/corn_jr_260m_v4_ft_social8`
    # reads 96/96 greedy parity for each against the pre-static-cache path, at
    # fp32, on the shipped weights. Priced on the 19-case checkup: decoding
    # turns 5,403 -> 5,169 ms with every row identical. `--no-buckets` and
    # `--no-compile` are the controls every card before 2026-09-07 was read
    # under. `prefix_reuse` stays off despite passing the same parity check --
    # it makes the decoder stateful across calls, and that is a property a
    # scorer should have to ask for (see corn/agent.py).
    buckets: bool = True
    compile_step: bool = True
    prefix_reuse: bool = False
    log: str = DEFAULT_LOG_STR
    logging: bool = True

    @classmethod
    def load(cls, path: Path | None) -> "ServerConfig":
        """Defaults, overlaid with a JSON file if there is one.

        A missing file is not an error -- a fresh clone has no `server.json`
        and must still run. A file that exists and is wrong is an error,
        loudly: the whole reason to have a file is that its contents take
        effect.
        """
        cfg = cls()
        if path is None or not Path(path).exists():
            return cfg
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConfigError(f"{path}: {exc}") from None
        if not isinstance(raw, dict):
            raise ConfigError(f"{path}: expected an object, got "
                              f"{type(raw).__name__}")
        known = {f.name for f in fields(cls)}
        # A retired key is dropped with a note rather than refused: the file
        # is the owner's, written when the key meant something, and a server
        # that will not start over a setting that no longer exists protects
        # nothing.
        for k in sorted(set(raw) & set(RETIRED)):
            print(f"config   !! {path}: '{k}' is retired -- {RETIRED[k]}; ignored")
            del raw[k]
        stray = sorted(set(raw) - known)
        if stray:
            raise ConfigError(f"{path}: unknown key(s) {stray} -- known keys "
                              f"are {sorted(known)}")
        for k, v in raw.items():
            setattr(cfg, k, v)
        cfg.validate()
        return cfg

    def override(self, args: argparse.Namespace) -> "ServerConfig":
        """The command line on top, and only where it was actually given.

        `None` from argparse means "not passed" and must not overwrite a
        file's value with a default. Every flag in `add_arguments` therefore
        defaults to `None`, and the dataclass holds the real defaults.
        `--all` is applied here rather than stored, so the file can never
        hold an `all` that disagrees with the three booleans it expands to.
        """
        for f in fields(self):
            v = getattr(args, f.name, None)
            if v is not None:
                setattr(self, f.name, v)
        if getattr(args, "all", False):
            # **`--all` fills in what was not asked for; it does not overrule
            # what was.** Until 2026-09-06 the three it expands to had no
            # negative flag between them, so "set all three" and "set the ones
            # nobody set" were the same statement. `--no-multi` arrived with
            # decision 6 and made them different: `--all --no-multi` read as
            # multi *on*, silently, which is the measurement control being
            # dropped on the floor rather than refused. An explicitly passed
            # flag is not None here, so honouring it is one condition.
            for name in ("search", "extract", "multi"):
                if getattr(args, name, None) is None:
                    setattr(self, name, True)
        self.validate()
        return self

    def validate(self) -> None:
        if not isinstance(self.port, int) or self.port <= 0 or self.port > 65535:
            raise ConfigError(f"port {self.port!r} is not a port")
        if self.dtype not in DTYPE_NAMES:
            raise ConfigError(f"dtype {self.dtype!r} is not one of "
                              f"{list(DTYPE_NAMES)}")
        if self.temperature < 0 or self.speech_temperature < 0:
            raise ConfigError("temperatures cannot be negative")
        # `corn.gate.willingness` is minus a probability, so every score it
        # can return lies in [-1, 0). A threshold outside that is not a tuning
        # but a switch nobody meant to throw: at 0 he never speaks, below -1
        # the gate is a no-op that still pays for a forward per window. The
        # sign is the easy typo and this is the guard for it.
        if not -1.0 <= self.gate_threshold <= 0.0:
            raise ConfigError(
                f"gate_threshold {self.gate_threshold!r} is outside [-1, 0] "
                "-- corn.gate.willingness returns minus a probability, so a "
                "positive threshold silences every window")
        if self.reader not in ("generate", "head", "head_whole"):
            raise ConfigError(f"reader {self.reader!r} is not `generate`, "
                              "`head` or `head_whole` -- see corn/reader.py")
        # `corn.reader`'s margin is a logit and has no natural range, so this
        # is a typo guard rather than a policy one: the two cross-validated
        # folds read -1.98 and -2.06, and anything an order of magnitude away
        # is a decimal point in the wrong place, not a tuning.
        if not -20.0 <= self.reader_threshold <= 20.0:
            raise ConfigError(
                f"reader_threshold {self.reader_threshold!r} is outside "
                "[-20, 20] -- corn.reader's margin is a verifier logit and "
                "the cross-validated folds read about -2")
        # The whole-passage margin is `max s - s_null` off one softmax, and the
        # two cross-validated folds read -1.09 and -1.25. Same kind of typo
        # guard as above, and a *separate* one because the two are separate
        # quantities: a reader who moved `reader_threshold` and expected the
        # whole arm to follow would be tuning a head that is not running.
        if not -20.0 <= self.reader_whole_threshold <= 20.0:
            raise ConfigError(
                f"reader_whole_threshold {self.reader_whole_threshold!r} is "
                "outside [-20, 20] -- the whole-passage margin is max s minus "
                "s_null and the cross-validated folds read about -1.2")
        if self.reader == "head_whole" and not self.reader_adapter:
            raise ConfigError("reader head_whole needs a --reader-adapter: "
                              "the head and its 160 deltas are one file and "
                              "there is no arm without it")
        # A negative tolerance would admit only pairs scoring *above* the
        # argmax, of which there are none, so the rule would silently be off
        # while reading as on.
        if self.reader_extent_d < 0:
            raise ConfigError(
                f"reader_extent_d {self.reader_extent_d!r} is negative -- 0 "
                "turns the extent rule off and there is nothing below that")
        if self.identity_check not in ("on", "log"):
            raise ConfigError(f"identity_check {self.identity_check!r} is not "
                              f"on or log")
        if self.family_check not in ("on", "log", "off"):
            raise ConfigError(f"family_check {self.family_check!r} is not "
                              "`on`, `log` or `off` -- see corn/socialfam.py")
        # The literal rather than an import of `corn.agent.Agent.SEED_TRIMS`,
        # for `DTYPE_NAMES`' torch-free reason; `check_serverconfig.py` holds
        # the two equal the way it holds the dtype names equal.
        if self.seed_trim not in ("off", "obs", "both"):
            raise ConfigError(f"seed_trim {self.seed_trim!r} is not `off`, "
                              "`obs` or `both` -- see corn/agent.py's "
                              "Agent.SEED_TRIMS for what each one costs")
        # Same restatement, same guard: `Agent.SEED_REPASS_MODES`.
        if self.seed_repass not in ("off", "always", "contaminated"):
            raise ConfigError(f"seed_repass {self.seed_repass!r} is not "
                              "`off`, `always` or `contaminated` -- see "
                              "corn/agent.py's Agent.SEED_REPASS_MODES")
        if not isinstance(self.round_reserve, int) or self.round_reserve < 0:
            raise ConfigError(f"round_reserve {self.round_reserve!r} is not a "
                              "non-negative token count")
        if not isinstance(self.budget, int) or self.budget <= 0:
            raise ConfigError(f"budget {self.budget!r} is not a positive "
                              "token count")
        if not self.ckpt:
            raise ConfigError("ckpt cannot be empty")
        if not isinstance(self.tools, list) or not all(
                isinstance(t, str) and t for t in self.tools):
            raise ConfigError("tools must be a list of tool names")
        if "decline" in self.tools:
            raise ConfigError("`decline` is not a member of tools -- it is "
                              "the `decline` key / --no-decline flag; see "
                              "corn.agent.declaration_names")

    def save(self, path: Path) -> None:
        """Write only the keys that differ from the defaults.

        A file holding thirty defaults is a file whose one real decision is
        invisible, and it silently pins values a later release may want to
        move. The studio writes through here; a hand edit that writes more
        still loads fine.
        """
        base = type(self)()
        out = {f.name: getattr(self, f.name) for f in fields(self)
               if getattr(self, f.name) != getattr(base, f.name)}
        Path(path).write_text(json.dumps(out, indent=2) + "\n",
                              encoding="utf-8")

    def as_dict(self) -> dict:
        return asdict(self)


def add_arguments(ap: argparse.ArgumentParser) -> None:
    """Every field as a flag, defaulting to `None`. See `override`."""
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                    help=f"JSON of the same keys; absent is fine "
                         f"(default {DEFAULT_CONFIG.name})")
    ap.add_argument("--ckpt", default=None, help=HELP["ckpt"])
    ap.add_argument("--host", default=None, help=HELP["host"])
    ap.add_argument("--port", type=int, default=None, help=HELP["port"])
    ap.add_argument("--device", default=None, help=HELP["device"])
    ap.add_argument("--dtype", default=None, choices=DTYPE_NAMES,
                    help=HELP["dtype"])
    ap.add_argument("--temperature", type=float, default=None,
                    help=HELP["temperature"])
    ap.add_argument("--speech-temperature", type=float, default=None,
                    help=HELP["speech_temperature"])
    ap.add_argument("--notes", default=None, help=HELP["notes"])
    ap.add_argument("--persona-state", default=None,
                    help=HELP["persona_state"])
    ap.add_argument("--birthday-lead", type=int, default=None,
                    help=HELP["birthday_lead"])
    ap.add_argument("--doc", default=None, help=HELP["doc"])
    ap.add_argument("--packs", default=None, help=HELP["packs"])
    ap.add_argument("--search", action="store_true", default=None,
                    help=HELP["search"])
    ap.add_argument("--extract", action="store_true", default=None,
                    help=HELP["extract"])
    ap.add_argument("--extract-gate", dest="extract_gate",
                    action="store_true", default=None,
                    help=HELP["extract_gate"])
    ap.add_argument("--no-extract-gate", dest="extract_gate",
                    action="store_false", default=None,
                    help="read every window and let the generator decide "
                         "whether to speak -- the pre-2026-09-01 behaviour, "
                         "and the control a gated card is read against")
    ap.add_argument("--gate-threshold", type=float, default=None,
                    help=HELP["gate_threshold"])
    ap.add_argument("--reader", default=None,
                    choices=("generate", "head", "head_whole"),
                    help=HELP["reader"])
    ap.add_argument("--reader-threshold", type=float, default=None,
                    help=HELP["reader_threshold"])
    ap.add_argument("--reader-extent-d", type=float, default=None,
                    help=HELP["reader_extent_d"])
    ap.add_argument("--reader-adapter", default=None,
                    help=HELP["reader_adapter"])
    ap.add_argument("--reader-whole-threshold", type=float, default=None,
                    help=HELP["reader_whole_threshold"])
    ap.add_argument("--multi", action="store_true", default=None,
                    help=HELP["multi"])
    ap.add_argument("--no-multi", dest="multi", action="store_false",
                    default=None,
                    help="answer every turn on an empty history -- the "
                         "runtime before 2026-09-06 and the control every "
                         "card written before it was read under")
    ap.add_argument("--seed-turn", dest="seed_turn", default=None,
                    help=HELP["seed_turn"])
    ap.add_argument("--seed-trim", dest="seed_trim", default=None,
                    choices=("off", "obs", "both"), help=HELP["seed_trim"])
    ap.add_argument("--seed-repass", dest="seed_repass", default=None,
                    choices=("off", "always", "contaminated"),
                    help=HELP["seed_repass"])
    ap.add_argument("--tools", type=_csv, default=None, help=HELP["tools"])
    ap.add_argument("--tools-dir", default=None, help=HELP["tools_dir"])
    ap.add_argument("--no-grammar", dest="grammar", action="store_false",
                    default=None, help=HELP["grammar"])
    ap.add_argument("--no-decline", dest="decline", action="store_false",
                    default=None, help=HELP["decline"])
    ap.add_argument("--no-fold", dest="fold", action="store_false",
                    default=None, help=HELP["fold"])
    ap.add_argument("--fold-history", dest="history_fold", action="store_true",
                    default=None, help=HELP["history_fold"])
    ap.add_argument("--no-fold-history", dest="history_fold",
                    action="store_false", default=None,
                    help="the control: drop an evicted turn whole, as every "
                         "card before 2026-09-07 was read")
    ap.add_argument("--no-confirm", dest="confirm", action="store_false",
                    default=None, help=HELP["confirm"])
    ap.add_argument("--restrict", action="store_true", default=None,
                    help=HELP["restrict"])
    ap.add_argument("--identity-check", dest="identity_check", default=None,
                    choices=("on", "log"), help=HELP["identity_check"])
    ap.add_argument("--name-header", dest="name_header", action="store_true",
                    default=None, help=HELP["name_header"])
    ap.add_argument("--family-check", default=None,
                    choices=("on", "log", "off"), help=HELP["family_check"])
    ap.add_argument("--round-reserve", type=int, default=None,
                    help=HELP["round_reserve"])
    ap.add_argument("--budget", type=int, default=None, help=HELP["budget"])
    ap.add_argument("--buckets", action="store_true", default=None,
                    help=HELP["buckets"])
    ap.add_argument("--no-buckets", dest="buckets", action="store_false",
                    default=None,
                    help="the control: attend the full block every step, as "
                         "every card before 2026-09-07 was read")
    ap.add_argument("--compile", dest="compile_step", action="store_true",
                    default=None, help=HELP["compile_step"])
    ap.add_argument("--no-compile", dest="compile_step", action="store_false",
                    default=None,
                    help="the control: capture the unfused decode step, as "
                         "every card before 2026-09-07 was read")
    ap.add_argument("--prefix-reuse", dest="prefix_reuse", action="store_true",
                    default=None, help=HELP["prefix_reuse"])
    ap.add_argument("--log", default=None, help=HELP["log"])
    ap.add_argument("--no-log", dest="logging", action="store_false",
                    default=None, help=HELP["logging"])
    # CLI-only, applied in `override` and never stored: a file key `all` that
    # disagreed with the three booleans it expands to would be the
    # two-descriptions failure this module exists to prevent.
    ap.add_argument("--all", action="store_true", default=False,
                    help="everything he can do, in one flag: --search "
                         "--extract --multi. Only the capability flags -- it "
                         "will never imply --no-confirm (a call that cannot "
                         "be taken back keeps asking first), nor the "
                         "measurement controls (--no-decline, --restrict, "
                         "--no-grammar, --dtype), because 'all of him' and "
                         "'a different experiment' are different requests")
