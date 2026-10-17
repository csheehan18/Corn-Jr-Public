# Thirty-eighth finding — the margin is diagnostic on every checkpoint except the one the gate was written for

**Cost:** 0 s of new scoring on record; it reads 5 cards scored for an earlier finding (`nano100m_v1`, `nano20m_v1`, `nano20m_v1_chat` and 2 more). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`scripts/margin_probe.py` on five checkpoints. **No training** — every one was already on disk,
and the whole read is a forward pass per item plus the generation the harness already does.

The question WS-B1 asked: at the position where Corn-Jr chooses between `<|call|>` and `<|say|>`,
is `logit(<|call|>) − logit(<|say|>)` smaller on the calls he should not make? If yes, an
inference-time gate buys abstention through the deference channel — let the call complete, refuse
to execute it, hand back `{"ok": false, "reason": "not_confident", "clarify": ...}` and let him
read it out. No training, no corpus, and no fighting a reflex that three arms have now failed to
suppress.

**The criterion was pre-registered in the script's docstring and committed before the first
number was produced** (`git show` on the commit preceding the run): *some threshold gates ≥50% of
the wrongly-emitted calls while catching ≤5% of `chat.engage`'s correct calls, on the `_chat` arm
checkpoints.*

## It fails on the arm it was written for and passes everywhere else

| checkpoint | arm | `oos` called | wrong calls | AUC | gated at ≤5% collateral | criterion |
|---|---|---|---|---|---|---|
| `nano20m_v1_chat` | `_chat` | 93/100 | 111 | **0.814** | 41.4% | **not met** |
| `nano20m_v1_chat_seed2` | `_chat` | 71/100 | 86 | **0.809** | 18.6% | **not met** |
| `nano20m_v1` | control | 95/100 | 118 | 0.954 | 77.1% | met |
| `nano20m_v1_seed2` | control | 100/100 | 120 | 0.936 | 70.0% | met |
| `nano100m_v1` | control | 85/100 | 103 | 0.888 | 61.2% | met |

AUC is the probability that a randomly chosen correct call outranks a randomly chosen wrong one,
ties counted half. It is reported beside the threshold number because the criterion's own axis is
a threshold and a threshold is not scale-free: a checkpoint whose margins are spread wider scores
better at a fixed collateral rate for reasons that have nothing to do with how separable the two
populations are.

**Read at matched scale and matched recipe, the separation is not marginal.** The two `mix_v1`
seeds at 29.6M read 0.936–0.954, a within-arm spread of 0.018. The two `mix_v1_chat` seeds at the
same scale read 0.809–0.814, a spread of **0.005**. The gap between the arms is 0.122 against
within-arm spreads of 0.018 and 0.005, which clears the thirtieth finding's bar comfortably.
`nano100m_v1` is a different scale and is not pooled into that comparison; at 0.888 it sits below
both `mix_v1` seeds and above both `_chat` seeds, which is the direction capacity would predict
and is one checkpoint.

**So the gate is not built.** That is what the pre-registration says to do, and doing it is the
point of having written it down first. WS-B2 is dropped from the plan.

## What is actually true about the margin

The direction is right on all five checkpoints and never in doubt: the correct calls are the
confident ones, by +2.55 to +3.76 of median margin. Nothing here says the margin is noise.

`chat.abstain_talk` is separated completely and on every checkpoint — ordinary conversation sits
at a median margin of −8.72 and −7.72 on the `_chat` seeds, against `chat.engage`'s +7.38 and
+5.06, and he calls on 0 and 0 of the 100 talk items. **He is not uncertain about whether a
sentence is a request.** The entire overlap is between `chat.abstain_oos` and `chat.engage` —
between "this is a request" and "this is a request I can serve" — which is the same boundary
every failing arm in the project has run into.

## The unwelcome part, which is why this is a finding and not a note

The treatment that improves the behaviour is the treatment that destroys the instrument. The
`_chat` arm is the one carrying `data/raw/chat.txt`; it abstains more often on `oos` (93 and 71
of 100 called, against the controls' 95, 100 and 85), and its remaining wrong calls are the ones
the margin cannot see. Training removed the wrong calls a gate would have caught and left the
confident residue.

If that reading is right, then the gate and the corpus compete for the same items, and a gate
priced on an untreated checkpoint is priced on mass that any successful arm will have eaten
first. That would make the whole inference-time route worth less than the 77.1% on `nano20m_v1`
makes it look.

**It is a hypothesis and n=5 does not establish it.** The abstention rate and the gate's yield do
not order together across the five (71 → 18.6%, 85 → 61.2%, 93 → 41.4%, 95 → 77.1%, 100 → 70.0%),
so "more abstention trained in, less left for the gate" is not a dose-response anybody measured
here — it is the arm distinction that is clean, and the mechanism behind it that is not. What
would settle it is a third `_chat` seed and the margin re-read on whichever of WS-C, WS-D or WS-E
actually moves an abstention row, which costs nothing beyond the probe once those checkpoints
exist.

## The name-phase reading, which was free and says something else

On the wrongly-emitted calls, mass at the first byte of the tool name is spread rather than
collapsed, and which tool it spreads onto is not stable across arms: `send_text` 0.61 /
`save_note` 0.49 on `nano20m_v1_chat`, `resolve_date` 0.44 / `web_search` 0.35 on
`nano20m_v1_seed2`, `web_search` 0.40 / `resolve_date` 0.31 on `nano100m_v1`. The masses do not
sum to one and are not meant to — names share prefixes, so a token is compatible with several and
the buckets overlap by construction.

Nothing here supports "he reaches for one tool when he is unsure". Whatever the wrong call is, it
is not a single default.

## What this does not settle

- **The 181 prefilled prompts were never in the instrument.** The plan asked for the margin over
  `evals/chat.jsonl` and "the selection items", but 181 of `tools.jsonl`'s 200 prompts end at
  `<|call|>` — the format hands them the call and there is no fork to read. Only the 19
  `tool is None` items contributed, so `tool.selection`'s share of every number above is 19 items
  and the 300 chat items are the instrument.
- **Greedy decoding, so the verdict joined to each margin is the argmax path.** A margin of +0.12
  and a margin of +8.9 both produce a call, and this measures how the decision was made rather
  than how it would have gone under sampling.
- **Two seeds per arm**, and the caution the thirty-seventh finding earned applies: a spread of
  0.005 across two points is not a floor. What makes this quotable is that the two arms do not
  overlap and the gap is seven times the wider within-arm spread — not that either spread is
  known.
- **Nothing here is a claim about whether a gate would work if it were built.** The criterion is
  about whether the margin can find the items; a gate also has to not break `chat.engage` in
  production, and that was never measured because the gate was never built.
