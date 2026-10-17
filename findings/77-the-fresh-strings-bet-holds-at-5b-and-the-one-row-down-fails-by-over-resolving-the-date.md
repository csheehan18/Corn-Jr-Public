# Seventy-seventh finding — the fresh-strings bet holds at 5B, and the one row that moves down fails by over-resolving the date

**Cost:** 3.1 min of scoring on the 1 card first cited here (`corn_jr_260m_v4`); it also reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn_jr_260m_v4` trained 2026-08-29 on a DigitalOcean H200 — commit
`4eae0dbc`, `configs/corn_jr_260m_v4.py`, `data/mix_v4_5b` verified onto the
droplet at the recorded sha256 before the run. 23,511.5 s at ~223k tok/s,
$22.47 of training. The control is `corn_jr_260m` — same shape, same schedule,
same token budget, both compiled, **the corpus the only variable** — and its
card `evals/results/corn_jr_260m.json` is quoted as committed; nothing was
retrained or re-scored. Full provenance in `260M Run Data v4/RUN-NOTES.md`.

What this run is the first evidence of, stated before the numbers:
`mix_v3_5b` re-read five of eight slices more than 7 times and three more than
27; `mix_v4_5b` regenerates them at held shares so nothing passes arm 2's
15.21-pass cost point and 95.3% of the budget is under the 3.6-epoch knee. The
bet, as `configs/corn_jr_260m_v4.py` put it: **fresh strings from the same
distribution are no worse than the same strings repeated.** No nano run could
see this — at 131M every slice is under a pass either way — so this is the
bet's first test, and there is one of it.

## The bet holds, on every instrument that can read it

`scripts/rowdiff.py` over the two cards: **68 of 121 shared quantities
reproduce identically**, including every row the repetition could have been
paying for:

    tool.copy        120/120 -> 120/120     identical
    tool.copy_wide   300/300 -> 300/300     identical
    temporal.copy    353/353 -> 353/353     identical
    refusal.say      270/270 -> 270/270     identical

Of the rows that moved, nearly all moved up: `tool.selection` 171 → 192,
`turn2.first` 171 → 192, `daylog.open` 4 → 83, `daylog.targeted` 4 → 31,
`daylog.empty` 0 → 26, `notefid.trained_phrasing` 74 → 99,
`notefid.novel_phrasing` 66 → 80, `chat.abstain_greet` 67 → 85,
`tool.name_fidelity` 106 → 112, `register.conv` 71 → 77. On the untouched
prose instruments: `lm.conversational` 0.2905 → 0.2880 and `lm.temporal`
0.1847 → 0.1641 improve; `lm.narrative` and `lm.web` give back 0.0011 and
0.0021 nats/byte; `variety.distinct3` 0.9108 → 0.9179 and `self_repeat`
0.026 → 0.0167 both improve. Fresh strings were not merely no worse; at equal
budget the corpus bought more.

(`val_loss` 1.5320 → 1.6046 is quoted nowhere above because it compares
nothing: the val stream went from eight sources to thirteen, four of them new
and harder than what they displaced.)

## The new families are in the base

Thirty-eight rows exist only on the v4 card. The ones with a corpus slice
behind them, against what the nano arms and the fine-tune vehicle managed:

| row | v4 base | the comparison |
|---|---|---|
| `turn2.react` /120 | **120** | nano MIX 112–117, FT 107–108 (finding 74) |
| `turn2.chain_result` /50 | **50** | nano 47–49 |
| `turn2.chain_ellipsis` /50 | 49 | nano 44–48 |
| `turn2.chain_pronoun` /50 | **40** | unreadable at nano (0–17 control); the 260M substrate carried it, as predicted |
| `turn2.reask` /96 | 40 | nano MIX 57–66 — partial; re-ask is again the hard axis |
| `turn2.reask_yn` /40 | 15 | nano MIX 33–38 — same |
| `compound.pipe` /48 | 36 | nano v2 arms 44–48 |
| `compound.pipe_first` /48 | **47** | nano 48/48 |
| `compound.items` /48 | 29 | — |
| `extract.span` /200 | **94** | `ftextract`'s installed 70 (finding 65) |
| `extract.abstain` /200 | 121 | `ftextract`'s 141 |
| `extract.paired` /128 | **117** | the row finding 70 built |
| `search.route_base`/`_heldout`/`_wide` /200 | **200, 200, 200** | perfect, held-out phrasings included |

Every family the corpus was rebuilt to install is present with no fine-tune —
extraction *above* what fine-tuning installed on the v3 base, routing at
ceiling on all three phrasings. Re-ask at its signed 0.14% one-pass share
lands under the nano mix arms, which had it at a far heavier relative weight;
whether re-ask wants a bigger share is a supply question the card only prices.
`packs.cell`/`column` read 8/72 and 7/88 with no packs slice in any corpus —
low is the expected reading, not a defect.

## The one row down, and its failure is one species

`daycross.with_day` 188 → 118 — seventy items, far outside the ~10-item
single-run wobble floor — while `daycross.no_day` goes 171 → 192. The `why`
buckets say what happened:

    daycross.with_day   v3: chose_resolve_date 5,  called_anyway 3, declined 4
                        v4: chose_resolve_date 67, called_anyway 14, chose_web_search 1
    daycross.no_day     v3: declined 9, wrong-tool 12, called_anyway 8
                        v4: declined 1, chose_schedule_personal_note 6, chose_resolve_date 1

**The failure is `chose_resolve_date`, 5 → 67 — one species is 82% of the
row.** He did not forget how to handle a dated request; he resolves dates too
eagerly, reaching for the tool when the day is already in the utterance. The
same training that did it shows on the other side of the pair: on `no_day`,
where resolving *is* the move, declines and wrong tools nearly vanish. Day
handling got stronger and now over-fires on the half where it should stand
down — finding 73's see-saw shape, arriving on the day axis.

The suspects are the day-heavy additions — `daylog_5b.txt` at 5.00% (whose
own rows went 4/200 → 83/200) and the day-context chat file — but at n=1
that is a hypothesis, not an attribution. What would separate it is the same
instrument P3-E used: a with-day/no-day matched pair on one carrier. Worth
noting alongside: `daycross` was already the one behaviour measured *worse*
at 91.6M than 29.6M (the scale-transfer caveat both 260M configs carry), so
this row was the pre-registered place to look for trouble.

`chat.abstain_oos` 33 → 14 is not a second flag: the owner retired that row
in favour of grid A's decline column (2026-08-27), and a drop against
decline-trained corpora is the documented expected reading.

## Instrument facts found while scoring

  * **`ckpt.pt` and `last.pt` are the same model** — every tensor
    `torch.equal`. DATA.md §9's "score both" question closes: their cards
    differ only in the `ckpt` path and in `turn2_reply`.
  * **Which means `turn2_reply` is not per-item-deterministic.** Identical
    weights moved that section and no other. A `turn2_reply` delta between
    checkpoints is not evidence until its seeding is pinned.
  * **The anneal replicated its own number.** select moved 0.1329 across the
    anneal against last run's measured 0.133 — `wsd`'s
    anneal-does-the-work observation, reproduced on a different corpus.
  * Both cards were scored on the droplet's H200 where every prior card was
    scored locally. Greedy decode is not formally bit-stable across GPU
    architectures; any row that reads strangely should be re-scored locally
    with `--only` before being believed. The rows quoted here were
    cross-checked against expectations from local nano runs and none reads
    strangely.

## Limits

n=1 — one seed, one run, no spread on anything above. The repetition repair
and the daycross regression are both single observations; finding 68 says
frozen-row seed variance at 260M-scale fine-tunes is small, but no second 5B
base exists to say it for pretraining. The read stands on the failure-species
structure, which seed noise does not produce.
