# Eight times the nudges reads worse; the short test had misled

**Full result:** A 5M that reads the control's 128.7M tokens in one pass at 6 rows a step instead of 48 -- 41,896 updates for 5,237 -- ends reading held-out text 0.193 nats a token *worse* than the two controls (3.235 against 3.041), where a fifth-of-a-run smoke of the same recipe had read 0.15 better. R was predicted "better" at nine in ten and is on the wrong side of level. The ruler's lift falls with it: 0.39 on the fields and 0.26 on the wishes, under every one of twelve ordinary 5Ms (0.43 to 0.59 and 0.30 to 0.39). U is down. Fields right 72 and wishes 60. Read by hand with the writers hidden, 24 of the ruler's sentences draw the same stock openings from this run and from the control on 22. One seed, one run, on the owner's terms.

**Cost:** config and reader committed with the pre-registration at 23:29 on 2026-11-14 (fbaa3e1), after five smokes of a fifth of a run (366.4 s of card) and their read (47.5 s); the run trained 359.4 s (the controls 350.0 and 353.9, contended), 549.2 s for the chain with a read that re-read twelve runs (175.9 s); the cause reads 44.4 s. ETA about seven minutes of training; 6.0.

**The question** (owner, 2026-11-14: "you're right that our models are not
being nudged enough", then "Yes let's do it"). Every small run takes 5,237
updates; the 260M took 203,451; nothing in the record had varied the count.
Two explanations of why he lacks what a count of his text knows were to be
told apart: next-piece reading does not pay for it (A), or it does, late,
and 5,237 updates stop short (B). The pre-registration is
`configs/nano5m_v3_webblend_nudge.py`'s docstring.

## The read

    held-out text is the mean of four sources on fixed windows; lift is how far the phrase moves the right
    label past the other offered labels, nats a frame

                                      held-out text   fields: right  lift    wishes: right  lift
    twelve 5Ms with no lesson         3.025-3.107        65-84   0.43-0.59      61-72   0.30-0.39
      the two controls                3.036, 3.047       79, 75  0.50, 0.51     68, 62  0.37, 0.30
    8x the updates, seed 1337         3.235                 72   0.39              60   0.26

* **R: worse.** +0.193 nats a token. The row's lines were "better", "level"
  and "between"; this is past all three on the other side. Predicted 0.06
  to 0.12 better.
* **U: down.** Both lifts are under every ordinary run. Predicted flat.
* **C.** 72 fields, inside the twelve's 65 to 84; 60 wishes, one under
  their lowest.
* **S.** His first word is the same with and without the phrase on 93 of
  141 fields; the controls 108 and 84.
* **H.** Marks written before the key was opened: 2 of 24 continuations
  carry what the phrase means for this run and 1 of 24 for the control
  ("a beautiful day" from both for a cheerful tune about sunshine; "a very
  difficult one" from this run for the detective's race). The other 45 are
  "best way to make it", "most important thing to do", "a great place to
  go", or the phrase's own noun.

## Why the smoke read the other way (cause reads, not registered)

Validation loss at the same tokens read, this run beside a run of the
control's recipe (finding 235's seed 1337, whose curve was on disk):

    tokens read      25M     49M     74M     98M     123M    129M
    6 rows a step    3.33    3.22    3.08    2.86    2.85    2.79   (step size 1.9e-3 falling to 2e-4)
    48 rows a step   3.30    2.98    2.84    2.71    2.64    2.60   (2.8e-3 falling to 3e-4)

In the full schedule the small step is never ahead, not even at 25M tokens,
where the smoke had it 0.15 ahead. The smoke was a whole schedule squeezed
into a fifth of the tokens: its step size had already fallen to its floor
by 25M, and at the floor a run with 8,000 updates behind it beats one with
1,000. Stretched to the full budget the step size stays high for most of
the run, and a small batch at a high step size sits on the noise of its own
steps. **The loss follows the step size down; it does not follow the count
of updates.**

That the end state is noise can be read off the two iterates the run saved,
896 updates apart:

    iterate 41,000          held-out text 3.2347   lift 0.39 and 0.26
    iterate 41,896                        3.2346        0.44 and 0.27
    their weights averaged                3.1893        0.42 and 0.26

Averaging two sets of weights takes 0.045 nats off. Neither iterate is
where the run is; both are scattered round somewhere better.

Reading and lift, every size, on the same windows: the 5Ms 3.04 and 0.52 /
0.35; this run 3.23 and 0.39 / 0.26; the 20Ms 2.88 and 0.54 / 0.42; the
260M 2.00 and 1.23 / 1.18.

## What it licenses

By the pre-registration, its third outcome: **R is not better, so nothing
is concluded about A against B.**

* **"Starved of updates" was wrong as put.** The control's batch is not
  wasting tokens over a full run: cut eight ways at a step size the smokes
  chose, the same tokens read worse. What limits a small step is its noise.
* **A short test flatters more updates, as it flatters a high step size.**
  The smokes were run to choose a step size and I read a result off them
  and gave nine-in-ten odds on it. A recipe read on a squeezed schedule is
  a read of the squeeze.
* **Where reading fell the lift fell with it.** Not evidence that better
  reading would raise it -- no 5M on these tokens has yet read clearly
  better than the controls, so that side is unread -- but the one run that
  moved reading moved the lift the same way.
* **Averaging is what this points at.** Two iterates averaged recover a
  quarter of the loss. Keeping a running average of the weights is the
  standard answer to noisy steps and costs no tokens, no pass and almost
  no time; whether many small steps with an average beat the control is
  untested, and needs a change to the training loop.
* **The hand read stands apart from the scores.** Whatever the recipe, a
  5M continues the ruler's sentences with the same few stock openings; the
  phrase reaches what he writes in 1 or 2 of 24.
* **Unguarded read.** No guard pins `scripts/read_nudge_arm.py`; its own
  check is the two controls' saved counts. The lift is a new instrument,
  bounded by twelve runs' spread and by nothing else.

**What it does not settle.** The same cut at a lower step size, or with the
step size taken to zero. A running average of the weights, at either batch.
Whether a 5M that does read clearly better on the same tokens has more
lift -- the question this run was built to ask and did not reach.

## Amended 2026-11-14 -- the run changed two things, and the cause above is not shown

The owner asked whether the failure had been investigated before it was
explained ("Did you investigate the failures first? To verify yourself?").
It had not been, beyond the curve and the two iterates. Checked afterwards
(probe only -- not on disk):

**Weight decay is applied a step, so eight times the steps is far more of
it.** Both runs set it to 0.1. Summed over the schedule the step sizes come
to 8.61 for the control and 45.93 here: a weight nothing else touched would
end at 0.42 of itself in the control and 0.010 of itself in this run. The
control's whole run is shorter than one decay time (6,080 steps at its mean
step size, of 5,237); this run is four and a half of them (9,122 of 41,896).

**The weights show it.** Root-mean-square size, this run beside six runs of
the control's recipe (the two controls and finding 235's four):

    group                this run    six ordinary runs
    word table           0.054       0.082 to 0.087
    position table       0.014       0.043 to 0.061
    attention weights    0.062       0.074 to 0.077
    mlp weights          0.059       0.084
    norm gains           1.51        1.00 to 1.05     (not decayed; grown to make up)

So the run cut the batch **and** regularised the model about five times as
hard, and ended with weights 20% to 75% smaller. The pre-registration called
it one variable and it was two.

**What this withdraws.** "What limits a small step is its noise" and "the
control's batch is not wasting tokens over a full run" are not shown: the
worse reading may be the decay, the noise, or both. The two-iterate average
(0.045 nats) shows some of it is noise and says nothing about the rest.
"The loss follows the step size down" described the curve and was offered as
the cause without a test.

**What stands.** The numbers of the read. That a squeezed smoke is not a
read of a recipe -- here for a second reason too: the smokes at 6 rows had a
full control's worth of decay behind them (a step-size sum near 8.8) and the
smoke at 48 rows almost none (1.6).

**The run that would say:** this recipe with the weight decay set so the
whole run applies what the control's does -- 0.1 x 8.61 / 45.93, about
0.019. Six minutes, config only. Until it is read, nothing is concluded
about more updates, in either direction.

**Read 2026-11-15: finding 237.** The rerun at 0.0188 overshot (weights
twice ordinary size) and reads 3.224: the decay was not the cause. Cooling
the end state recovers 0.03: nor was end noise.
