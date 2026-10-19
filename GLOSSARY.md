# Glossary

**Doc-status:** reference — the in-house words a reader meets in the findings, each in one plain sentence

**This exists because the findings are written in a working vocabulary.**
181 findings were written by the people running the experiments, for each
other, and the words that saved them time cost a stranger the whole page. An
outside read on 2026-10-18 named it first: "ft4g", "the door", "copy band",
"own quads" and "RULES 21" were unreadable from a skim. Every finding now
opens with a headline in plain words; this page is for everything under it.

**The first list is enforced.** `scripts/check_findings.py` reads every bold
term under "Words a headline never uses" and fails if one appears in a
finding's headline (its first line), whole word, any case, with or without a
plural `s`. It also fails on a headline longer than 12 words, or one carrying
a backtick or an underscore, because those are code names. A new in-house word
goes in that list the day it is coined, with its sentence.

"He" throughout is the model, Corn-Jr. That is a choice and not a slip.

## Words a headline never uses

- **arm** — one training run in an experiment, differing from its control in exactly one thing; most findings compare two or more arms.
- **nano** — the project's small model sizes (about 20M to 30M parameters), used to test an idea cheaply before it reaches the 260M model.
- **slice** — one source of training data inside the mix: web text, dialogue, tool transcripts, generated worlds.
- **payload** — the new data a fine-tune adds, trained alongside a replayed sample of the original mix.
- **row** — one test in the frozen evaluation set, scored as a count such as 353 of 353.
- **card** — a scorecard: the result file from scoring one checkpoint on every frozen test.
- **ruler** — a measuring instrument built for one property (vocabulary, output variety, register) where no test existed.
- **gate** — a threshold an experiment must pass to continue, written down before it runs.
- **bar** — a threshold a result must clear to count as a win, written down before it runs.
- **kill** — a pre-registered failure line; crossing it ends the experiment.
- **rung** — one step of the tag-language ladder (docs/PLAN-TAG-LANGUAGE.md); each rung is a capability tested in order.
- **hatch** — a runtime shortcut that answers a matched request by keyword rule instead of asking the model.
- **door** — the point where the runtime takes over: once he writes a tag, the runtime holds what follows to the grammar that tag allows (finding 131).
- **carrier** — the wording around a request's content: the sentence frame ("can you look up ...") or, in a multi-part request, the linking word that joins the parts (finding 145).
- **copy discipline** — whether he copies a tool's answer word for word instead of writing one from memory.
- **copy band** — how far the copy test may fall before an experiment is rejected; finding 170 showed it was measuring seed noise.
- **quad** — a test item of four prompts (the original, the result flipped, the options swapped, and both), counted right only when all four are (finding 169).
- **binding line** — a line he writes before choosing, naming which option the condition selects (finding 175).
- **one-slot line** — a binding line naming only the selected option; a two-slot line names both, and costs him the word "not" (findings 176-178).
- **flip word** — a word that reverses which option a condition picks, such as "not" or "unless" (finding 173).
- **RULES 21** — rule 21 in docs/RULES-SIMPLIFIED.md: nothing may train him to produce what the runtime writes for him.
- **ft4g** — the 260M fine-tune (recipe 4, variant g) that served before the social fine-tune replaced it.
- **social8** — the 260M checkpoint fine-tuned with social replies; the model that ships in v0.5.
- **Population A** — the 721 whole Natural Questions passages the passage reader is scored on, exactly as the runtime sees them (finding 87).
- **A-CLEAN** — the 319 answerable passages of Population A on which at least four human annotators agree.
- **residue** — the passages the reader still gets wrong.
- **span head** — the trained boundary model that marks where in a window an answer starts and ends (finding 83).
- **reduce** — the rule that turns per-window answer candidates into one answer for the passage.
- **extent rule** — the rule that decides how far to widen a found answer, for example to take in a trailing unit.
- **grounded** — the runtime check that an answer is copied word for word from the source text, not invented.
- **see-saw** — the trade-off where training him to serve more requests made him decline fewer, and the reverse (finding 67).
- **vehicle** — how new data is delivered: mixed into pretraining, or added later by fine-tune (finding 60).
- **toolgrid** — a harness instrument that runs hundreds of live turns over a grid of tool requests; **searchgrid** and **chaingrid** do the same for search phrasings and multi-step chains.
- **searchgrid** — see toolgrid.
- **chaingrid** — see toolgrid.

## Words that are safe in a headline

These are ordinary machine-learning words, or project words plain enough to
read cold. They are here so a reader can check, not because they are banned.

- **seed** — the random starting point of a training run; two seeds of the same experiment show how much a number moves by chance.
- **noise floor** — how far a score moves between seeds with nothing else changed; a difference inside it is not a result.
- **pretraining / fine-tune** — training from nothing on the full mix, against a short extra training run on top of an existing model.
- **mix** — the blend of data sources and their shares that a model is pretrained on.
- **20M, 50M, 260M** — model sizes in parameters; 260M is the size that ships.
- **checkpoint** — a saved model at one point in training.
- **runtime** — the program around the model that builds its prompt, enforces formats, runs tools and talks to the user.
- **tag / label** — a short marker he writes to say what kind of move or request comes next, which the runtime can then enforce.
- **parse** — his own breakdown of a request into parts and groups, written as a line before he acts.
- **template** — a reusable task shape the runtime offers him, shown as a description he picks from.
- **window** — a fixed-length chunk of a document, the unit the passage reader reads.
- **reader** — the model plus its trained head that finds the answer to a question in a document.
- **checker** — a second trained model that decides whether the reader's answer should be said or withheld (in older findings, the verifier).
- **move** — the kind of social reply he is making: greeting, consolation, farewell, and so on.
- **depth** — how many levels of nesting a request has.
- **held-out** — test items whose wording or content never appeared in training.
