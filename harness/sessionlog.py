"""Every turn, structured, one JSON line each -- the corpus half of a session.

**`Saved Sessions/*.txt` is for a person and this is for a corpus builder, and
neither can be the other.** Those files are pasted terminal: prose, timings,
`->` and `<-` gutters, and a `<|say|>` whose words might have been written by
the model, by a tool, or by a runtime pool with nothing to tell them apart.
That is the right shape for reading back what happened and the wrong shape for
training on it, and the distinction cannot be recovered afterwards -- by the
time a turn is text, who wrote which span is gone.

So this writes the same turns again in the shape the thing they are *for*
needs: the user's utterance exactly as typed, the calls he wrote, the payloads
the tools returned, and a `say` carrying `corn.agent.SAY_AUTHORS` provenance.
`corn/agent.py`'s `SAY_AUTHORS` comment has the argument for why that field
decides whether a logged conversation is usable at all; the short version is
that two of its three values are text the model must never be trained to
produce, and a transcript cannot tell you which you have.

**On by default, and that is the decision worth defending.** Every other flag
in `harness/server.py` that changes what the instance *is* defaults to off,
because each of them changes behaviour the user would notice. This one changes
nothing a turn does -- it is a file append after the answer has already gone
out -- and its failure mode is the one `/saved` already has: a session worth
keeping is only kept if somebody remembered to keep it, and a training corpus
you have to remember to collect is one you do not collect. `--no-log` turns it
off for a sitting.

**It lands in `Saved Sessions/`, which `.gitignore` already covers**, under the
rule stated there for `notes.jsonl` and `contacts.json`: what a running
instance accumulates belongs to the person running it, not to the artefact
everyone else clones. These are real conversations and they are the most
personal thing this repo produces.

One line per turn, appended and flushed as it happens rather than assembled at
exit. A server that is killed mid-sitting -- which is how a resident process
usually ends -- keeps every turn up to the last one.
"""

from __future__ import annotations

import itertools
import json
import os
from datetime import datetime
from pathlib import Path

# Beside the prose transcripts, for the reason the module docstring gives: they
# are two renderings of the same sitting and separating them by directory would
# only make them harder to line up.
DEFAULT_LOG = Path("Saved Sessions") / "turns.jsonl"


# **A counter, because the timestamp alone is not unique and the pid does not
# help.** The obvious id is time plus `os.getpid()`, and it is wrong here: the
# pid belongs to the *server*, which is resident, so every connection for the
# life of the process carries the same one. Two clients connecting inside the
# same second -- which `harness/checkup.py` does routinely, and which a
# reconnecting voice client would do constantly -- would then share a session
# id, and their turns would interleave under it as though one person had said
# all of them. Caught by `scripts/check_server.py` asserting that two
# connections are two sittings.
_counter = itertools.count(1)


def session_id(when: datetime | None = None, seq: int | None = None) -> str:
    """A name for one client connection, sortable and unique within a process.

    Sortable because the first thing anyone does with a pile of these is put
    them in order; the counter is what makes it unique. `seq` is for the guard,
    which needs the same id twice to prove the format rather than the clock.
    """
    stamp = (when or datetime.now().astimezone()).strftime("%Y%m%dT%H%M%S")
    return f"{stamp}-{os.getpid()}-{next(_counter) if seq is None else seq}"


def turn_record(session: str, turn: int, user: str, events: list[dict],
                wiring: dict, ms: float,
                when: datetime | None = None) -> dict:
    """One turn as a row, built from the events the runtime already emitted.

    Pure, and takes the event list rather than a live agent, so
    `scripts/check_server.py` can assert on the shape with no socket, no
    checkpoint and no GPU -- the same reason `split_emission` is pure.

    **Nothing here is derived by re-reading the transcript.** Every field is
    lifted from the event that carried it, because the events are what the
    runtime knew at the time and the transcript is what survived. That is the
    entire point of the file: a corpus builder that had to re-parse
    `<|say|>` out of `transcript` would be back to guessing who wrote it.
    """
    say = next((e for e in reversed(events) if e.get("t") == "say"), None)
    done = next((e for e in reversed(events) if e.get("t") == "done"), None)
    return {
        "ts": (when or datetime.now().astimezone()).isoformat(timespec="seconds"),
        "session": session,
        "turn": turn,
        # **The scarce half.** Everything else in this row can be regenerated
        # from a corpus; a real utterance in the user's own words, spelling and
        # register cannot, and it is the reason to keep any of this.
        "user": user,
        # **What the model was actually handed, when that is not what was
        # typed.** `corn.agent.fold_turn` casefolds an all-caps utterance and
        # drops a terminal question mark before the turn reaches the weights
        # (owner decision 1b/0), so from the day it landed the `user` field
        # above stopped being the string the turn was answered from. Both are
        # kept and `user` stays raw, because the raw utterance is the scarce
        # half and a fold is reproducible from it.
        #
        # `None` on every turn the fold did not change, which is nearly all of
        # them -- so the column is present exactly when there is a difference,
        # the rule `model_draft` and `author` already set. A count over `user`
        # that ignores this field is a count over two surface populations at
        # once, which is the failure the field exists to make visible.
        "folded": next((e.get("folded") for e in events
                        if e.get("t") == "fold"), None),
        "say": None if say is None else {
            "text": say.get("text", ""),
            "author": say.get("author"),
            "deferred": bool(say.get("deferred")),
            # Why his own social reply was refused, on the turns where one was
            # attempted and lost. `None` on every other turn, including under
            # `--restrict` where he was never asked -- the two are different
            # facts about a sitting and the field keeps them apart. This is the
            # column that makes "how often can he hold a social turn" a count
            # rather than an impression.
            "fell_back": say.get("fell_back"),
            # A family miss the runtime served anyway (PLAN-CONVERSATION 4a):
            # the reply carried no marker for the family the hatch matched,
            # on a family the check is not hard on -- or on any family under
            # `--family-check log`. `None` on every other turn, the rule
            # `fell_back` set; this is the column that makes the log-only
            # replay a number rather than a re-run.
            "soft_reject": say.get("soft_reject"),
            # Characters the frame-loss floor withheld, on the turns where the
            # emission carried no say marker at all and the user was handed a
            # floor instead. `None` on every turn that kept its frame -- this
            # is the column that makes "how often does he fall out of the turn
            # vocabulary" a count rather than an anecdote.
            "frame_loss": say.get("frame_loss"),
            # **What he wrote, on the turns where the user heard something
            # else.** `author` says an intervention happened; this says what it
            # cost, which is the column the seventy-eighth finding needed and
            # did not have. Without it a runtime- or tool-authored turn
            # discarded the model's own emission unrecorded, and every rate in
            # that audit -- how often the pool beat him, what the deferred say
            # replaced -- had to be measured against a second server running
            # different flags rather than read off these rows.
            #
            # `None` on every turn where his words were the words served, so
            # the field is present exactly when there is a difference to count.
            # Old rows have no key at all and read the same way, which is the
            # rule `author` on `calls` already set.
            "model_draft": say.get("model_draft"),
            # What the placeholder fill did to the sentence (PLAN-PERSONALITY
            # §4c): `filled`, or the reason it refused -- `no_user`,
            # `user_twice`, `placeholder`. `None` when the sentence had no
            # hole, which is every turn on a checkpoint before arm 9, so old
            # rows and new rows read the same way. `scripts/harness_ledger.py`
            # reads it as the `placeholder` rule's fire count.
            "placeholder": say.get("placeholder"),
            # The record he wrote under the say (PLAN-TAG-SPINE §2b, phase D):
            # `asked`, `answered` or `open`, or `None` on a turn he wrote no
            # line under -- every turn on a checkpoint before the line
            # trained, and every runtime-authored turn. Beside `author` and
            # `fell_back` for the reason those are here: a column gone by the
            # time a transcript is a file cannot be counted later, and this is
            # the one that says whether the record was written at all.
            "state": say.get("state"),
            # The identity hatch's own line, on a turn it stepped aside from
            # under `--identity-check log` (PLAN-PERSONALITY §7). `None` on
            # every other turn; the ledger reads it as the rule having fired
            # with the model's words served.
            "identity_pool": say.get("identity_pool"),
        },
        "calls": [
            # `author` arrived with the temporal hatch: a call the runtime
            # wrote is a row nothing may train on, exactly as a runtime `say`
            # is, and the moment the runtime knows that is the moment it is
            # recorded. Absent means the model decoded it, which was the only
            # possibility before the field existed -- so old rows and new rows
            # read the same way.
            {"raw": e.get("raw"), "ok": bool(e.get("ok")), "why": e.get("why"),
             "name": e.get("name"), "arguments": e.get("arguments"),
             "masked": e.get("masked", 0),
             "author": e.get("author") or "model"}
            for e in events if e.get("t") == "call"
        ],
        "obs": [
            # `read` is present only where a passage was read in windows, and
            # it is the complete record: the `fell_back` above is the last one
            # of these in a turn, which is the headline and not the count. A
            # sitting's extraction rate is this column, grouped.
            {"name": e.get("name"), "payload": e.get("payload"),
             "read": e.get("read")}
            for e in events if e.get("t") == "obs"
        ],
        "rejected": [e.get("why") for e in events if e.get("t") == "rejected"],
        "error": next((e.get("why") for e in events if e.get("t") == "error"),
                      None),
        # The raw turn text, kept whole and kept last. It is the thing a corpus
        # builder will actually tokenize, and it is deliberately *not* the only
        # thing here -- see the fields above.
        "transcript": None if done is None else done.get("transcript"),
        "outcome": None if done is None else done.get("outcome"),
        "ms": round(ms, 1),
        # **What the context was, not just what was said into it.** A row
        # whose tool set, checkpoint or `--multi` state is unknown cannot be
        # compared with another row, and a corpus assembled across a flag
        # change would silently mix two different questions -- the mistake
        # `declaration_names` documents for `tool.selection`.
        "wiring": wiring,
    }


class SessionLog:
    """An append-only JSONL sink, or nothing at all.

    `path=None` is a fully working no-op rather than a branch every caller has
    to remember: `--no-log` hands one of these over and `harness/server.py`
    calls it exactly as it would call a real one.
    """

    def __init__(self, path: Path | None, wiring: dict | None = None):
        self.path = Path(path) if path is not None else None
        self.wiring = dict(wiring or {})
        self.session = session_id()
        self.turns = 0
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, user: str, events: list[dict], ms: float) -> dict | None:
        """Write one turn. Returns the row, or `None` when logging is off.

        **A logging failure must never take a turn with it.** The answer has
        already gone to the user by the time this runs, so a full disk or a
        read-only path is a reason to say so once and carry on, not a reason to
        turn a good turn into a traceback -- the same argument `harness/
        server.py` makes for catching everything around `agent.turn`.
        """
        if self.path is None:
            return None
        self.turns += 1
        row = turn_record(self.session, self.turns, user, events,
                          self.wiring, ms)
        try:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        except OSError as exc:
            print(f"-- session log unwritable ({exc}); continuing without it")
            self.path = None
            return None
        return row
