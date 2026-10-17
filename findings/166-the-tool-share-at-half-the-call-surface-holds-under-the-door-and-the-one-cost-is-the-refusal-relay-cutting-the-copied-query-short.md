# One hundred and sixty-sixth finding — the tool share (ROADMAP TS): with `tools` and `toolspace` at half their share the call surface holds under the door at both seeds -- `tool.selection` 190 and 180 against 186 and 182, the routing rows 199-200 against 188-200 -- and nothing is a kill; the one registered cost is `refusal.say` at both seeds, read by hand as the relayed refusal cutting the copied query's last words short on four of the row's six strings; a quarter splits on `search.route_heldout` and is a direction

**Cost:** 70.5 min of training four nano runs (17.5-18.2 min each, `card_cost.py`; registered ~16-18), 11.8 min scoring their four standard cards and 6.8 min re-reading the full cell's two, 80.5 min of the staged read on six checkpoints (13.2-13.7 min each), all inside one hold of the card of 2.86 h against a registered ~3 h -- contended throughout (the card at 34-45% before the job), so every timing is a bound; the routing control 13.1 min and the hand-read probe 20 s on top; the build about 20 min of CPU (08:07-08:27 on 2026-10-13).

ROADMAP TS, PLAN-TAG-SPINE §7, the owner's D12 (2026-09-26: it runs for 1.0,
to find room in the mix for D10's layers). Pre-registered in
`configs/mix_v3_ts_half.py`'s docstring and committed at 2df7e96 before a
byte of either cut trained. One variable: the share of `tools`
(`tools_names_parse.txt`) and `toolspace` (`toolspace_decline_composed_parse.txt`)
in A2's tagged world, every other source byte-identical and `max_iters`
scaled with the budget so every other slice keeps its exposure:

    cell      tool share   max_iters   checkpoints
    full      5.15%        5,896       nano20m_v3_a2_on{,_seed2}   (A2's on cell, finding 150; re-read, not retrained)
    half      2.64%        5,744       nano20m_v3_ts_half{,_seed2}
    quarter   1.34%        5,668       nano20m_v3_ts_quarter{,_seed2}

Seeds 1337 and 2337, `compile=True`. Read by `scripts/run_ts.py` in one
sitting -- the standard card on all six (the full cell's as `__ts_card`) and
`scripts/probe_a2.py --families ts` on all six -- and tabled by
`scripts/read_ts.py`, written before the staged cards existed. **Cards:**
`evals/results/nano20m_v3_ts_{half,quarter}{,_seed2}{.json,__ts.json,__ts_items.jsonl}`,
`evals/results/nano20m_v3_a2_on{,_seed2}{__ts_card.json,__ts.json,__ts_items.jsonl}`.
`probe_a2.py` is held by `scripts/check_parseline.py` and nothing more:
**every staged number is a bound** (rule 28).

## Readable

Neither unreadable condition fired. Every primary of the full cell reads
188-200 of 200 bound (the bar was 160), and the full cell's re-read is the
2026-10-04 card to the item on every staged row it shares with it
(`tool.selection` 186 and 182 both days) -- the instrument did not move under
the arm.

## The registered read

A cell falls (`v`) when it is below the full cell at its seed by more than
`probe_move.half_width` at the full cell's rate. Seed 1337 then 2337.

    PRIMARY, bound              full        half         quarter
    tool.selection            186  182    190  180     183  181
    search.route_base         200  200    200  200     200  200
    search.route_wide         200  200    199  199     200  200
    search.route_heldout      197  188    200  196     192v 197

    KILL, forced card
    tool.copy_wide            299  299    297v 300     298  299

    HOLD, bound
    compound.pipe              45   29     46   39      40v  31
    compound.pipe_first        46   35     46   44      44   37
    turn2.chain_ellipsis       42   44     46   46      45   45
    turn2.chain_result         50   50     50   49      48v  50
    turn2.react               117  119    113v 120     115  113v
    turn2.reask                53   48     57   51      58   36v

    HOLD, forced card
    refusal.say               263  266    245v 260v    259  255v
    refusal.clarify            40   40     40   33v     40   40

**Half: every primary holds at both seeds and the kill does not fire**
(`tool.copy_wide` 297 against 299 at one seed -- two items of 300, a split,
not a kill). **One hold row falls at both seeds: `refusal.say`** (245 and 260
against 263 and 266). The table's row for that is **"a hold row falls at a
cut that otherwise holds -- that cut costs the row's turn: read row by row
beside D1, not a kill of the cut."** `turn2.react` and `refusal.clarify` fall
at one seed each.

**Quarter: `search.route_heldout` falls at one seed (192 against 197) and
holds at the other** -- "seeds split on a primary: a direction; no third
seed." So "room to a quarter" is not licensed. Five hold rows fall at one
seed each and none at both.

**The prediction, scored**: half holds every primary -- right; quarter holds
`tool.selection` -- right; quarter drops `route_heldout` -- at one seed, a
split; no kill -- right; `refusal.say` falls at the quarter -- wrong cell: it
fell at half at both seeds and at the quarter at one.

## Read by hand (EXPERIMENTS §5.6)

**`refusal.say` is a copy row with six answers on the side that fell.** The
row relays a refusal a tool handed over, word for word (`score_say`, exact
match). Its `no_results` items are 43 items over **six** strings ("I couldn't
find anything useful for {query}."), and a scratch decode of all 150 say
items (probe only -- not on disk) reads the full cell 150 and 146, half 125
and 140, **every lost item `no_results`**. At half seed 1337 all 25 lost
items are one failure: **the relayed sentence cuts the copied query's last
words** -- "...for what the loft smells." for "...what the loft smells like.",
"...which sock." for "...which sock is missing.", "...what my dentist had."
for "...what my dentist had for breakfast." -- on four of the six strings.
It is EXPERIMENTS §5.7's caution about `tool.copy` (six answers, one garbled
string costs twenty items) on a different row. The 232-answer
`tool.copy_wide` holds at both cuts, so the truncation is a real cost on the
relay of a long query and **not** the copy band falling. It is the cost this
finding hands D1, at its size.

**The quarter's `route_heldout` fall is a carrier that already misroutes.**
Seed 1337's eight misses: six `place_call` on "give me the discoverer of
Peliholm, please" and its kind, two `save_note`. The full cell's seed 2337
misses the same carrier the same way twelve times, and the quarter's seed
2337 improves on it (197 against 188). One carrier, read as a call, moving
between seeds -- not the share.

**The forced card's call rows rose with the cut**, side column and not the
read (finding 150: on the tagged cell the forced card is a transcript shape it
never trained): `search.route_base` 122 and 86 full, 200 and 154 half, 178 and
176 quarter. Fewer tool documents carrying a `parts:` line under every user
turn make the untagged forced prompt less foreign. The staged rows are the
read.

## Post hoc, not in the table: the social side

`probe_a2.py`'s guard family (finding 150's post hoc rows) reads, bound:

    row                    full        half         quarter
    social.bare_nocall    80   86     63   76      75   73
    social.voice          47   66     37   50      69   52
    social.family          7   13     11    8       8    3
    social.self           47   47     47   47      47   47

`social.bare_nocall` is below the full cell at all four cut checkpoints,
past the half-width at three; `social.voice` falls at half at both seeds and
splits at the quarter (69 up, 52 down) -- not dose-monotonic. Read by hand at
half: chit-chat draws a `web_search` or `resolve_date` call more often (15 and
15 `web_search` against 6 and 8), and his own social sentences drift into the
registry tools' say register -- "Listen to write a small agent on the user's
behalf.", "Note down that the loft was done.", "I'll call you the small agent
on the user's behalf." My guess at the mechanism, untested: toolspace's
plain-spoken declines and coined-tool says were a large share of the say
lines in the mix, and halving them leaves the registry tools' few say
templates a bigger share of what a say sounds like. **Not registered, so a
direction, and it names what a share cut has to watch beside the call rows:
the social turn.**

## What it licenses

**For D1's table: the tool slices can go to half their share** -- 2.64% at
nano, which is about 2.65% of `mix_v4_5b` against today's 5.3% (`tools`
0.59% + `toolspace` 4.7%), about 2.6 points of a 5B run, some 130M tokens, for
D10's layers. The surface the door holds does not need the rest: tool choice,
routing, call validity and the payloads' rows hold at both seeds. **The cost
goes into D1 with it, at its size**: the relay of a long refused query loses
its last words on a six-string row (`refusal.say` 245 and 260 of 270), and,
post hoc, the social turn's no-call and voice rows fall at half. **A quarter
is a direction and is not licensed.**

**What it does not settle.** Nano, A2's tagged world, with the door held by
the runtime (`probe_a2.py`'s *bound*): the untagged world was not cut, and
the reading is about the call surface *when the door holds*, which is the
question D12 asked. 260M has flipped a nano sign before (finding 51); D11's
pilot is where the share is read again. And whether the social side is the
share or the say register of what was cut is a probe -- a cut that keeps
toolspace's say lines and drops its calls separates them.

**Next** (not run): that separating probe, priced at four nano runs (~1.2 h)
plus the guard-family read; and PLAN-1-0 §10's share table carries the half
cut with its two named costs when D1 is taken.
