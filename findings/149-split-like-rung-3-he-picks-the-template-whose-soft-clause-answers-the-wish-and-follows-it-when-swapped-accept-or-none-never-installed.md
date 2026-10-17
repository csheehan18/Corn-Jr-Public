# One hundred and forty-ninth finding — rung 4 passes split like rung 3: when the runtime drops every template failing a clause it can check, he picks the one whose soft clause answers the request by meaning, 254 and 254 of 432 held-out combinations against a gate of more than 175 and arm F's 147 and 152, and the pick follows the wish when the wish is swapped -- while the accept-versus-none decision installed in no arm, and arm U's failed gate was a zero-shot paraphrase test whose one real selection rode on the template names' words

**Cost:** about 2.7 h of GPU on 2026-10-02 -- 2.4 h training eight nano runs at 17.4-19.5 min each (arms U, UD-id, UD-ev and US, two seeds; registered at 17-18 min a seed, so on its ETA) and about 20 min of scoring and probes between 11:08 and 17:08 (the cards, the full re-score, the swap and the trained-frame reads); corpus builds and floors on CPU, minutes. Amended 2026-10-03 with arm USN: 36.2 min of training two seeds (`card_cost.py` on the copy-wide cards, against a registered 17.5 min a seed), about 5 min of `prepare_mix`, the six checkpoints' scorer and swap and two copy-wide cards (11:31-12:12 end to end, the chain's log), and about 4 min of trained-frame probes, plus about 15 min of hand-read decodes (`probe_templates_usn_decode.py` on four checkpoints).

PLAN-TAG-LANGUAGE §6 rung 4 (ROADMAP G4), templates accept, deny and near
misses, read 2026-10-02. Four arms, each arm F's mix with a template payload
added on top, two seeds each (1337, 2337), arm F re-scored beside every one
and never retrained: **arm U** (template names, `use when`, `requires`;
`use: <name>|none`; `configs/mix_v3_funcworld_templates.py`), **UD-id** and
**UD-ev** (no names, a per-frame id; `use: <id>` and `use: because[<use
when>] <id>`; `..._templates_id.py`, `..._templates_ev.py`), and **arm US**
(rung 4 split like rung 3; `..._templates_us.py`). Each was pre-registered in
its config before a byte trained. The story of the day is in the commits
`24ff732` through `b202d4e`, and every number in them says where it was
measured.

**Cards** (`evals/results/`, committed unless said): arm U greedy
`<ckpt>__templates.json`; every option in full `__templates_full.json`;
UD `__templates_{id,ev}_full.json`; US `__templates_us_full.json` (arm F's
two land with this finding); `__copy.json` and `__copywide.json`.
**Instruments**: `scripts/probe_templates.py` (greedy, bound and free),
`probe_templates_full.py`, `probe_templates_desc_full.py`,
`probe_templates_us_full.py`, and `probe_templates_us_swap.py`. Their rows
are re-derived by `check_templates.py` (sections 6, 8a-8b, 9); the probes
themselves are held by no guard, and the swap script by nothing at all, so
**every number below is a bound** (rule 28). The trained-frame reads and the
swap's output are **probe only -- not on disk**.

## Arm U, as registered: the gate failed, and the hint verdict was printed

Bound greedy `use:` on the held-out cell, 320 frames:

    checkpoint   right / 320   right accepts / 208   near-miss false accepts / 192   forgery sig / name / none
    U s1             110             4                       15                         3 / 7 / 86
    U s2             115            12                        6                         2 / 4 / 89
    F s1             112            15                        8                         4 / 7 / 81
    F s2              93            50                       52                        24 / 23 / 39
    selector         141            59                       39                        27 / 14 / 54

Gate: more than 158 of 320 at both seeds. **It failed**, and the registered
row it landed on -- does not pass, the forgery not a decision, the selector
passes -- licenses "the runtime selects". The near-miss column read 15 and 6
against the selector's 39, and the forgery read `name` over `sig` at both
seeds, finding 130's prediction ("the name leads -- a hint").

## Read by hand (EXPERIMENTS §5.6): the cell made every string new

**The held-out, near-miss and forgery cells drew every clause and every name
word from held-out pools** -- none of their 2,400 strings appears in training,
which uses 34 clause strings -- so the gate asked for zero-shot paraphrase,
not selection. Unseen name spellings cost about 20 nats against `none`, so
greedy said `none` on 193 and 188 of 208 accept frames: **110 and 115 are the
always-`none` answer** (majority reads 112), the near-miss column is low
because he accepted almost nothing, and the hint verdict rested on about ten
non-`none` picks of 96. Scored in full -- every option's log-prob, no greedy
-- the same cells read at chance: selection 97 and 87 of 208 against 86.67
(arm F 88 and 93), and the forgery even, `sig` 36 and 42 against `name` 43
and 37.

**On frames he trained on** (181 accept frames from his own corpus, probe
only): selection installed, 102 and 118 of 181 against chance 74 (arm F 67);
accept-versus-none did not, AUC 0.54 and 0.59 against arm F's 0.53. So the
eval was the problem for selection, and the decision itself was not in the
weights.

## Re-scored on trained vocabulary, unseen combinations (`7299645`)

`evals/funcworld_templates_combo.jsonl`: all 34 trained clauses and 28 trained
name words, every shown (clause set, name) pair unseen as a right template. A
(domain, field, concept) triple hold-out was impossible: the corpus trains all
72. Every option in full, total log-prob:

    checkpoint   selection / 208   AUC accept-vs-none   near-miss FA / 192   forgery name / sig
    U s1              129               0.548                 60                 59 / 27
    U s2              130               0.579                 75                 51 / 34
    F s1               73               0.531                  0                 40 / 45
    F s2               77               0.530                  1                 39 / 41

Chance on selection is 86.67 (above it means more than 100). **Selection
installed** -- and the forgery says by what: where a template's name and its
`use when` disagree he follows the name 59 and 51 times against the
signature's 27 and 34, while arm F splits evenly. A hand read of eight forged
rows came out 4/4 (probe only), so the word is "leans on the name", not
"ignores the signature". Near-miss false accepts, 60 and 75 of 192, sit
around the selector's 62. **Accept-versus-none never installed** (0.55, 0.58
against arm F's 0.53).

**The cheap-predictor floor stops being usable here**: a bag of word pairs
fitted on the training frames reads 0.978 on these rows, because on trained
vocabulary the right template's words co-occur with the request's in
training. The combo numbers are read against chance and arm F only.

## Names gone: selection falls to chance (`43d5cb4`, `738ca27`)

The owner, 2026-10-02: no names -- descriptions with a per-frame id he
returns, "a clean option for runtime to use as well". UD-id and UD-ev train
arm U's 19,795 frames frame for frame, names and `requires` removed; they
differ only in whether `use:` writes the id alone or the chosen `use when`
copied whole, then the id.

    combo cell, 208 accept frames   total   per-token   AUC     picks id 1 / 320
    UD-id s1                          79       79       0.471      266
    UD-id s2                          78       78       0.479      199
    UD-ev s1                          98       93       0.460      153
    UD-ev s2                          97      101       0.502      176
    arm U (on UD-id rows)          89, 79                0.47      0, 47
    arm F (on UD-id rows)          89, 88           0.45, 0.51  205, 318

**At chance in both formats** (more than 100 needed; of the twelve readings
-- four checkpoints, three scores -- only UD-ev seed 2 per-token clears it,
at 101, and its total reads 97), and on their own training frames too:
74-86 of 181 against chance 74 (probe only). UD-id leans on id 1 (266 and 199
of 320 against chance 133). Accept-versus-none stays near 0.5. The registered
adoption row (id-only if it reads as well as UD-ev) lands on "below", but it
compares two nulls and decides nothing. **Arm U's selection was the names.**

## Arm US: rung 4 split like rung 3 (`e6597ee`, `a8d545a`)

Owner-approved the same day, on rung 3's lesson (finding 148): **he selects,
the runtime enforces**. The runtime checks every clause it can -- domain and
the hard field -- and drops the templates that fail; the ones it shows agree
on both word for word and differ only in the soft concept clause, of which
exactly one answers the request's soft term by meaning. He writes the clause
he matched, then its id; `none` is the runtime's (nothing survived) and he is
never trained to write it:

    template 1: use when a bar or a pub, a minimum rating, a hushed interior
    template 2: use when a bar or a pub, a minimum rating, a converted mill
    template 3: use when a bar or a pub, a minimum rating, a bustling scene
    <|user|>look for a place for drinks in Varunthgard, preferably steeped in the past, rated above 3
    parts: find
    use: because[a converted mill] 2

**Held out by combination**: phrasing `pi` of each concept never trains
beside the clause of its held-out family -- 24 of 72 (phrasing, clause)
pairings, rung 3's Latin square -- and never beside a distractor it would be
new beside either; all 24 clause strings train. **Two shortcuts the guard
caught before anything trained**: rung 3's decoy rule let a lookup on the
shown clause set alone score 0.984 of the held-out cell, and a per-request
distractor draw gave one concept a 0.454 prior against chance 0.333. Both
closed (one square for every concept, clash-free sets drawn first) and
`check_templates.py` section 9 fails on either.

Every option in full, total log-prob:

    cell (n)              chance   US s1   US s2   F s1   F s2
    train (432)             156     429     429    158    158
    heldout (432) -- gate   156     254     254    147    152
      2 templates (144)      72      96     100     64     66
      3 templates (144)      48      77      83     45     51
      4 templates (144)      36      81      71     38     35
      right over each distractor (864 pairs)   620     605    422    429
      picks id 1             156     147     163    135    202
    distractor (240)         96     147     156     89     88

**The gate is passed at both seeds**: 254 and 254 against more than 175, and
above the stricter bar a word-pair counter sets (more than 188); per-token
reads 259 at both. Arm F is under the gate at both seeds, so the rows do not
leak. There is no position habit (picks id 1 at 147 and 163 against 156),
and the near-meaning distractor cell reads 147 and 156 of 240 against
chance 96 and arm F's 89 and 88 -- not gated, because the hand-picked near
table carries a concept prior (0.558) no balanced table could remove.
Trained pairings read 429 of 432; held-out ones 254 -- he learned the
pairings and carries a good share of them to new ones, not all.

**The wish-swap** (`scripts/probe_templates_us_swap.py`, probe only). Each
held-out request's soft phrase is replaced with the first phrasing of a shown
distractor's concept (one that does not clash with the gold's), templates
kept -- 432 rows, none skipped. If he reads the wish, the pick should leave
the gold and land on the new wish's template:

    checkpoint   gold picked   new wish's template picked
    US s1        254 -> 35       106 -> 370
    US s2        254 -> 32       102 -> 372
    F s1         147 -> 151        --

**The pick follows the wish**; arm F does not move. The swapped phrasing is a
first phrasing and not held out, so 370 and 372 are read for direction, not
as a second held-out score.

**The copy kill.** As registered, `tool.copy` under 118 of 120 at both seeds:
US reads 98 and 104, so **the registered kill fired**. Each seed's failures
are one answer ("the Mekong"), and arm F's own seed 1337 reads 102 of 120,
all one answer ("Alexander Fleming"); on the 232-answer `tool.copy_wide` row
US copies 292 and 293 of 300 against arm F's 280 and 288. **On 2026-10-02,
after this read, the owner moved the standing kill to `tool.copy_wide`
against arm F** (EXPERIMENTS §5.7), where US is above arm F at both seeds.
That is a rule changed after the numbers it applies to were seen, and it is
written down as such; the argument for it is the row, not this arm -- six
answers, about twenty items an answer, and a control that fails the old line
itself. Arms U, UD-id and UD-ev read 120 at one seed or both and never fired
the old line.

## What it licenses

**G4 passes in the split design** (owner decisions, 2026-10-02):

* **Templates are shown as `template <id>: use when <clauses>`** -- no names,
  no `requires`. The runtime filters every clause it can check and owns
  `none`.
* **He judges the soft clause**, written description first, then the id:
  `use: because[<clause>] <id>`. The SPEC-LANGUAGE §7 amendment follows.
* **Who selects**: he does, among what the runtime lets through -- "he
  selects, the runtime enforces". PLAN-TAG-LANGUAGE §7's second kill cannot
  fire: the runtime selects on every checkable clause, and he selects on the
  one it cannot.

**What it does not show.** The accept-versus-none decision -- deny when
nothing fits, deny a near miss -- installed in no arm, on held-out, combo or
trained frames (AUC 0.46-0.59 everywhere, arm F 0.45-0.53); in this design it
is the runtime's, and a soft-only near miss is something he ranks rather than
refuses. Matching three clauses at once: arm U's combo selection was the
names. A held-out string: every US clause trains, only the pairing is new.
Anything at 260M. Nano, the synthetic world, one corpus construction per
arm, and a hand-built scorer.

## Amended 2026-10-03 -- arm USN: a soft `none` taught directly does not install either

Arm USN (`configs/mix_v3_funcworld_templates_usn.py`, pre-registered at
804bec1, run 2026-10-03): arm US plus soft-none frames, 30% of frames,
where every shown template passes the runtime's checks and none of their
concept clauses answers the wish -- `use: none<|end|>`. The question was
whether the one decision US learned, matching the soft clause, carries a
refusal when nothing matches. Scored by `scripts/probe_templates_usn_full.py`
on `evals/funcworld_templates_usn.jsonl`, total log-prob; the cards are
`evals/results/<ckpt>__templates_usn_full.json` and `__templates_usn_swap.json`:

    checkpoint     held-out AUC   trained-cell AUC   selection   false accepts   over-deny   copy_wide
    USN 1337           0.585           0.921           248/432      22/216        384/432    297/300
    USN 2337           0.588           0.923           266/432       2/216        424/432    291/300
    US  1337           0.579           0.915           254/432     216/216          0/432
    US  2337           0.603           0.859           254/432     216/216          0/432
    F   1337           0.502           0.478           147/432       0/216        432/432
    F   2337           0.479           0.508           152/432       0/216        432/432

(`false accepts` and `over-deny` are the probe's whole-line ranking, and are
not what he writes -- read below.)

**The registered row: AUC at or under 0.704 at both seeds -- a soft `none`
does not install at nano; `none` stays the runtime's** (D-A1.16, which
already gave it there). Neither control clears 0.704, so the rows do not
leak by the config's test. Selection held (248 and 266 against a bound of
234) and the copy band held (297 and 291 against arm F's 280 and 288).

**The trained cell is not a refusal, and the table's "learned the trained
pairings' refusals" row does not license.** By the letter it fires -- above
0.704 trained, under it held-out, both seeds -- but **arm US, which never saw
a `none`, reads 0.915 and 0.859 there**. The AUC is of (best template -
`none`), and on a trained pairing his best template is simply very sure of
itself when its clause answers the wish; that margin separates the rows
whether or not `none` was ever written. Read on the frames USN trained on
(`scripts/probe_templates_usn_traces.py`, 600 frames from the first 99% of
the payload, 433 accept and 167 none; probe only -- not on disk):

    checkpoint     AUC total   AUC per token   none on top: none frames / accept frames
    USN 1337         0.921         0.877                160/167 / 279/433
    USN 2337         0.943         0.944                166/167 / 405/433
    US  1337         0.929         0.799                  0/167 /   0/433
    US  2337         0.861         0.739                  0/167 /   0/433

By total log-prob the none frames add nothing over the confidence US already
has on the very frames they trained; per token they add a little (0.88 and
0.94 against 0.80 and 0.74). The `none on top` column says what a whole-line
ranking does, not what he writes -- the next section.

**Read by hand, and what it changed** (EXPERIMENTS §5.6). The first draft of
this amendment was written off the cards and the trained-frame table, with
two of seed 1337's printed rows glanced at, and said USN "learned to write
`none`". The hand read says otherwise. Twenty-two of seed 1337's rows were
read whole (ten held-out none, eight held-out accept, four near-none: every
option's score and the greedy `use:` line), then every row's greedy line was
classified and the decode's own first decision scored, on both USN seeds and
both US seeds (`scripts/probe_templates_usn_decode.py`; probe only -- not on
disk):

    checkpoint   first token: AUC held-out / trained cell / trained frames   none wins (none rows, frames)   free none (none rows / accept rows)
    USN 1337           0.547 / 0.559 / 0.587                                   0/216, 0/167                      0/216 / 1/432
    USN 2337           0.542 / 0.507 / 0.556                                   0/216, 0/167                      0/216 / 0/432
    US  1337           0.501 / 0.521 / 0.482                                   0/216, 0/167                      0/216 / 0/432
    US  2337           0.487 / 0.484 / 0.498                                   0/216, 0/167                      0/216 / 0/432

* **He never writes `none`.** The first token after `use: ` is `none` or
  `because[`, and `none` never wins it -- not on a held-out row, not on a
  trained row, and not on one of the 167 none frames he trained on. Its
  margin separates none rows from accept rows at 0.54-0.59, a few hundredths
  over arm US, which never saw it. **The refusal did not install even on the
  frames that taught it.**
* **The cards' over-deny and false-accept columns are the instrument.** Every
  template line opens `because[`, so the mass a decode puts on writing *some*
  template is split across two to four lines, while `use: none<|end|>` keeps
  its own whole; ranked line against line, `none` tops 384 and 424 of 432
  accept rows that the decode answers with a template on 431 and 432. The
  AUC column, a per-row margin, is not moved by that split the same way and
  stands as registered; the decision, false-accept, over-deny and `top=1`
  columns of `probe_templates_usn_full.py`, and the swap's `none on top`
  counts, are not reads of what he writes.
* **On a none row he takes a shown template or names one that is not
  there.** Seed 1337 takes a shown clause on 110 of 216 and writes an unshown
  one on 106 -- 102 of them a clause of the wish's own concept ("full of
  energy" -> `because[a bustling scene]`, with no such template shown). That
  is not a hidden refusal: he does it on accept rows too (130 of 432), and
  arm US does it as much (134 of 216 none rows, 187 of 432 accept). It is the
  wish's concept recalled, not copied off the menu.
* **On accept rows the concept is mostly right and the words often are not.**
  Free, seed 1337 writes the gold clause on 155 of 432 and another clause of
  the wish's concept, not on the menu, on 130 -- the right kind of place on
  285 (seed 2337 307, US 344 and 317), the copy of the shown words on about
  half of them. CLAUDE.md's rule, again: score structure and vocabulary apart.
* **The template id after the clause is not read here either.** Where he
  copies a shown clause, the id is that clause's own on 91 of 287 and 97 of
  295 (US 84 of 237, 118 of 312) -- about one in three, chance at two to four
  templates. Finding 148's amendment found the same of rung 3's letter; this
  is that split, owed there, read on rung 4's free decode.

**What it says, plainly.** Given a few clauses, he can tell which one fits a
wish best, even on pairings he never saw -- by kind, if not always by the
menu's own words. He cannot tell that none of them fits: taught 30% `none`,
he never once writes it, even on the frames that taught it. And he does not
reliably write the number of the template he chose. At nano, `none`, the copy
of the shown words and the id are the runtime's: the bind (`use_usn_accepts`)
already limits him to a shown pair or `none`, and the id can follow from the
clause.

**What it does not say.** That a refusal cannot train at all: one share
(30%), one construction, no dose. Anything at 260M. That the runtime can read
`none` off his confidence -- arm US's own held-out AUC is 0.58-0.60 on the
whole-line margin and 0.49-0.50 on the first token.
