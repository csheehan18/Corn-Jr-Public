# Corn-Jr

Corn-Jr is a 260M-parameter language model I trained from scratch to be a
personal assistant that runs on one machine and gets things done by calling
tools: web search, calls, texts, notes, date resolution. Everything was built
for it: the tokenizer, the training corpus, the model, and the runtime around
it. It all runs on a single RTX 3080.

The project is also a research log. Every experiment gets a numbered write-up
called a **finding**, and there are 178 of them here. They record what I
expected, what happened, and what I got wrong, including the experiments that
failed. This repo holds those findings and the runtime code. The training code
and weights are not included yet.

## Start here

You don't need to read 178 findings. These are the ones I'd point anyone to
first, grouped by what they taught me.

### Models take the cheapest route the data allows

- **[Finding 12](findings/12-the-copy-discipline-does-not-generalise-and-the-corpus-is-why.md)
  and [Finding 13](findings/13-invent-the-world-and-the-copy-discipline-generalises.md).**
  The model was supposed to answer from what the search tool returned. It got
  27 of 120 right. The cause was the training data: the search tool only knew
  28 facts, each seen about 107 times, so the model could memorise the answers
  and never read the tool's output. I replaced them with about 8,700 invented
  facts, each seen once or twice. Same model, same token count: 120 of 120.
  The model did exactly what the data rewarded.
- **[Finding 158](findings/158-memorise-or-learn-is-readable-off-the-data-wordings-seen-more-than-ten-times-are-labelled-from-memory-and-a-settled-carrier-is-learned-as-a-list.md).**
  You can tell before training whether a dataset will teach an idea or a
  lookup table. At this scale, a wording seen more than about ten times gets
  answered from memory. If a cheap feature, like the first two words, settles
  the answer, the model learns a list and fails on anything new.

### Check the measurement before believing it

- **[Finding 53](findings/53-the-envelope-decides-the-output-too-and-two-of-my-checks-were-reading-the-harness-as-the-model.md).**
  Two of my own checks were grading the harness, not the model. One rejected a
  correct answer ("Looks like 1538 degrees Celsius.") because "looks like"
  wasn't on its list of allowed phrasings. The other blamed the model for
  answers that a token limit had cut off.
- **[Finding 145](findings/145-the-depth-wall-under-the-windowed-runtime-is-the-carrier-word-and-re-presenting-the-uncovered-gap-takes-arm-s-to-095-and-089.md).**
  The model seemed unable to build nested structures more than one level deep.
  Reading every failure by hand showed it was one
  phrase, "two things", that it treated as plain text. With "the pair" instead,
  it reached depth ten on 52 to 54 of 54 chains. The structure was learned and
  only the wording was wrong.
- **[Finding 170](findings/170-the-copy-bands-standing-kill-measured-seed-noise-seeds-of-one-arm-spread-up-to-54-items-and-the-band-was-3-to-4.md).**
  My rule for calling an experiment a failure assumed run-to-run noise of 3 or
  4 items out of 300. Retraining the same setup with different random seeds
  showed noise of up to 54, so two failures it had already called couldn't be
  told apart from noise. I rewrote the rule and added an automated check that
  enforces it.

### What worked

- **[Finding 112](findings/112-the-trunk-fine-tuned-on-whole-passages-reads-five-hundred-and-thirteen-and-five-hundred-and-ten-on-two-seeds-and-the-bidirectional-flip-without-adaptation-reads-under-the-frozen-reader.md)
  and [Finding 117](findings/117-the-whole-passage-adapter-reader-ships-and-the-runtime-reads-526-of-721-at-half-the-latency-with-the-three-passages-over-the-replay-traced-to-the-harvests-bf16-trunk.md).**
  Pulling the answer out of a web page was the weakest step. A small adapter
  that reads each page whole raised correct answers from 389 to 513 of 721 on
  one seed and 388 to 510 on a second. It shipped and reads 526 of 721 in the
  live runtime.
- **[Findings 175](findings/175-his-binding-line-installs-he-reads-the-flip-words-beside-the-request-on-92-to-99-percent-and-the-pick-reads-the-line-but-crossing-it-with-the-result-does-not-form.md),
  [176](findings/176-the-two-branch-binding-line-closes-the-pick-every-quad-right-on-a-right-line-and-a-forged-line-followed-576-of-576-and-the-gate-passes-on-all-three-the-line-is-the-wall-now.md)
  and [177](findings/177-the-runtimes-else-slot-does-not-bring-the-negation-read-back-the-first-slot-stays-at-0-68-and-the-one-slot-lines-0-94-is-the-best-binding-on-record.md),
  read in order.** Teaching the model to handle "if it's raining, X, otherwise
  Y". In 175 it learned to write the plan correctly, `if: raining -> X`, on
  92 to 99% of new prompts, but still followed that plan 60% of the time when
  it wasn't raining. In 176 the plan names both branches, and choosing the
  right one works for the first time. Writing the longer plan got harder,
  though, especially for negated conditions. 177 tested one explanation for
  that and ruled it out.

## How the research is run

- **Predictions come first.** More than half the experiments are written down before
  training starts: what will change, what result counts as a pass, and what
  counts as a failure. That way the result can't move the goalposts.
- **Findings are permanent.** Numbers never change and nothing is deleted.
  When a later finding overturns an earlier one, the earlier one says so at
  the top and stays.
- **Read the raw output first.** Before a number gets reported, a sample of
  the model's actual outputs is read by hand. Several times in this log, the
  measurement turned out to be wrong when the model was not.
- **Automated checks guard against silent failures.** The main repo has about
  100 scripts that catch the failures that never raise an error, such as a
  dataset that quietly mislabels 2% of its examples.

The findings refer to the model as "he". That's a habit from the project, not
a claim about the model.

## What's in this repo

| Folder | What it is |
|---|---|
| [`findings/`](findings/) | All 178 findings. [`findings/README.md`](findings/README.md) is the full index. |
| [`harness/`](harness/) | The runtime: the server, tool backends, the local web app ("the studio"), the voice client, and the evaluation suites. |
| [`corn/`](corn/) | The parts of the model code the runtime needs: the model, decoding, tools, and the answer reader. |
| [`tokenizers/`](tokenizers/) | The tokenizer the model was trained with. |
| [`docs/MODEL-CARD.md`](docs/MODEL-CARD.md) | What release 0.5 can and can't do, with measured numbers. |
| [`VISION.md`](VISION.md) | What the project is aiming for. |

**Not included:** the model weights, the training code, the data generators,
and the corpus. Without weights the runtime will start but has nothing to
load.

## Running it

It was built on Python 3.11 with PyTorch and CUDA. Install PyTorch for your GPU
first (the top of [`requirements.txt`](requirements.txt) shows how), then:

```
pip install -r requirements.txt
pip install "starlette>=0.37" "uvicorn>=0.29" websockets
python -m harness.studio
```

The studio is a local web app for chatting with the model and managing its
settings. On first run it asks for a checkpoint.

## License

Apache 2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

Built by Conner Sheehan ([GitHub](https://github.com/csheehan18)).
