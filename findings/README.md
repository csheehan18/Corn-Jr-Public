# Findings

**Every experiment this project ran, one file each, numbered in the order they
were made.** Each headline below is the result in plain words, at most twelve
of them. Open a finding and its first line under the headline, **Full
result**, is the precise version, numbers and all. The files are working
records, written in the project's own vocabulary; [GLOSSARY.md](../GLOSSARY.md)
defines every in-house word in one sentence. "He" is the model.

One file per finding, in the order they were made. The prose below is the
running summary that used to open the README — it is the same text, and it is
the fastest way to see what the whole sequence adds up to.

These findings lived in `README.md` until they were split out here. The
numbering did not change: where a config docstring or a note elsewhere says
"README's twelfth finding", it means finding 12 in the table below.

**The table is an index and nothing else, since 2026-09-08.** Its third column
had grown to 178 KB of summary — 81 entries longer than 400 characters, one
longer than 8,000 — so opening the index cost more than opening a finding, and
an index nobody scans is how two findings came to share the number 115 for
three days. Every one of those summaries is in
[SUMMARIES.md](SUMMARIES.md), verbatim and in order; what is left here is the
number, the finding's own title, and the link. Each row's title is parsed from
the finding's own first line, so the two cannot drift apart.

`scripts/check_findings.py` holds all of it: numbers unique, the index
complete and sorted, a summary for every finding, and every "finding *N*"
citation in the tree resolving to one that exists.

| # | Finding |
|---|---|
| 0 | [The small training pipeline runs end to end with no code changes](00-phase-0-pass-condition.md) |
| 1 | [Five times the parameters costs only a third of the decode speed](01-first-finding.md) |
| 2 | [Decode speed is launch overhead per layer; CUDA graphs remove most](02-the-extrapolation-measured.md) |
| 3 | [Training and validation loss never separate on one pass of data](03-what-a-clean-loss-curve-is-worth.md) |
| 4 | [A frozen evaluation set, and the three problems it caught](04-a-ruler-and-the-three-things-it-caught.md) |
| 5 | [The tool-call format must be in pretraining, and costs about 3%](05-the-format-has-to-be-in-pretraining-and-it-costs-about-3.md) |
| 6 | [Fine-tuning installs the tool format but not using the tool's answer](06-the-format-fine-tunes-in-fine-deferring-to-the-tool-does-not.md) |
| 7 | [Real web text improves prose but not using the tool's answer](07-real-language-moves-prose-and-does-not-move-deference.md) |
| 8 | [An 8k BPE tokenizer reads 3.8x more text per token](08-the-tokenizer-is-worth-3-8x-and-the-reason-to-fear-it-isnt-real.md) |
| 9 | [BPE's compression becomes a better model; a fifth comes from context](09-the-compression-converts-and-about-a-fifth-of-it-is-context.md) |
| 10 | [A generated tool dataset caps at 2.3 MB of distinct examples](10-the-tool-slice-and-what-a-generator-cannot-buy.md) |
| 11 | [A twenty-fifth of the planned tool data buys most of the behaviour](11-a-25th-of-the-declared-share-buys-most-of-the-behaviour.md) |
| 12 | [Copying fails to generalise because the training facts were memorisable](12-the-copy-discipline-does-not-generalise-and-the-corpus-is-why.md) |
| 13 | [Inventing the fact database makes him copy tool answers perfectly](13-invent-the-world-and-the-copy-discipline-generalises.md) |
| 14 | [The JSON data taught the format but not copying field names](14-the-same-bug-a-third-time-and-the-rule-it-settles-into.md) |
| 15 | [The two measured data shares were 4 to 25 times too large](15-both-shares-were-four-to-twenty-five-times-too-big.md) |
| 16 | [A new output-variety metric, and a data change that didn't move it](16-the-ruler-for-output-variety.md) |
| 17 | [One test moved 18 items on the random seed alone](17-the-row-that-never-moved-moves-eighteen-items-on-the-seed-alone.md) |
| 18 | [That 18-item swing was one fact; the test held only six answers](18-a-hundred-and-twenty-items-six-answers.md) |
| 19 | [The noise floor across four seeds, and which past readings it erases](19-the-noise-floor-measured-and-what-it-costs-the-back-catalogue.md) |
| 20 | [No data share moves copying above noise](20-copy-discipline-is-not-a-lever-any-share-moves.md) |
| 21 | [Copying is a step: it appears once any tool data exists](21-copy-discipline-is-a-step-and-the-step-is-the-slice-existing.md) |
| 22 | [Every conversation dataset fails a vocabulary test built from web text](22-everything-that-sounds-right-fails-the-ruler.md) |
| 23 | [The vocabulary test really measures how much web text is mixed in](23-the-bar-measures-how-much-web-is-in-the-corpus.md) |
| 24 | [The rejected dialogue data costs prose quality and nothing else](24-the-slice-the-bar-rejected-costs-prose-and-nothing-else.md) |
| 25 | [Dialogue data buys conversational vocabulary, not conversational style](25-the-slice-buys-conversation-and-does-not-buy-register.md) |
| 26 | [He knows where a turn ends; the long replies were our fault](26-he-knows-exactly-where-a-turn-ends-and-the-35-was-ours.md) |
| 27 | [The first data mix with every share measured, not guessed](27-the-first-corpus-nobody-inherited.md) |
| 28 | [Tool routing was template matching; deferring to the tool was not](28-routing-was-template-matching-deference-was-not.md) |
| 29 | [More phrasing templates fix only the phrasings that were added](29-the-boundary-is-a-set-and-enlarging-it-mostly-enlarges-the-set.md) |
| 30 | [Noise levels belong to a training setup, not to a test](30-a-floor-is-a-property-of-the-arm-not-of-the-row.md) |
| 31 | [The gain has no sharp threshold, and the fix was already cheap](31-there-is-no-knee-and-the-intervention-was-already-cheap.md) |
| 32 | [A bigger phrasing test; its no-transfer reading was later withdrawn](32-the-bucket-works-at-n-398-and-the-transfer-is-still-zero.md) |
| 33 | [Copying depends on the tool output's shape and nothing else](33-the-copy-behaviour-is-keyed-to-the-payloads-shape-and-to-nothing-else.md) |
| 34 | [He picks tools he never saw in training, but can't say no](34-he-routes-to-tools-he-was-never-trained-on-and-cannot-decline.md) |
| 35 | [One percent of non-tool turns teaches him when not to call](35-the-corpus-never-showed-him-a-turn-that-does-not-call.md) |
| 36 | [Reply length inflates the measured style gain, but the gain survives](36-the-length-confound-is-real-and-small-and-turn-one-was-the-control.md) |
| 37 | [Training second-turn declines changed nothing and cost tool choice](37-the-turn-two-class-moved-turn-two-abstention-by-exactly-nothing-and-cost-the-tool-choice.md) |
| 38 | [A confidence margin spots wrong calls, except where it was needed](38-the-margin-is-diagnostic-everywhere-except-on-the-arm-the-gate-was-for.md) |
| 39 | [Restricting names to declared tools fixes routing, not refusal](39-narrowing-buys-the-routing-completely-and-buys-the-refusal-not-at-all.md) |
| 40 | [Moving the date header recovers about ninety items it was costing](40-decorrelating-the-day-header-recovers-ninety-of-the-hundred-and-twenty-six-it-was-costing.md) |
| 41 | [Too noisy to read; underneath, wrong contact names fell 19 to 2](41-the-row-cannot-read-it-and-the-substitution-fell-from-nineteen-to-two.md) |
| 42 | [He now declines 118 times, with routing untouched](42-he-declines-a-hundred-and-eighteen-times-and-the-routing-underneath-is-untouched.md) |
| 43 | [Two extra seeds already on disk retire three earlier readings](43-the-two-extra-seeds-were-already-on-disk-and-the-floor-they-measure-retires-three-readings.md) |
| 44 | [The last unmeasured data share costs nothing; web gains are linear](44-the-last-unpriced-share-costs-nothing-and-the-web-response-is-linear.md) |
| 45 | [The first full data mix keeps every separately measured effect](45-the-phase-one-corpus-assembles-and-every-separately-measured-effect-survives-it.md) |
| 46 | [A dataset was missing a class; one test passed by reciting](46-a-slice-on-disk-was-four-per-cent-short-of-its-generator-and-a-hard-zero-turns-out-to-be-recitation.md) |
| 47 | [The leading learning rate finished last; 3e-4 stays](47-the-rate-that-leads-for-sixty-per-cent-of-the-probe-finishes-last-and-the-decision-rule-had-an-unmeasurable-term.md) |
| 48 | [Four bugs let decoding escape the call grammar mid-call](48-four-ways-the-constraint-could-not-finish-a-call-and-the-mask-that-costs-most-when-it-forbids-least.md) |
| 49 | [Second-turn data teaches him to talk, at a cost to deferring](49-the-second-turn-learns-to-talk-and-pays-for-it-in-deference.md) |
| 50 | [Invented facts make him copy; a real name brings memory back](50-the-index-was-invented-and-the-world-is-not-so-a-real-name-reopens-the-weights.md) |
| 51 | [At 260M the date header helps where at 30M it hurt](51-the-header-that-cost-ninety-nine-items-now-buys-seventeen-and-the-scorecard-and-the-runtime-disagree.md) |
| 52 | [Of 25 search phrasings taught, he kept about four](52-the-corpus-taught-twenty-five-phrasings-and-four-of-them-carry-the-tool.md) |
| 53 | [Two of my checks were scoring the harness, not the model](53-the-envelope-decides-the-output-too-and-two-of-my-checks-were-reading-the-harness-as-the-model.md) |
| 54 | [Batch decoding 32 to 128 windows: both predictions about why were wrong](54-thirty-two-windows-to-a-hundred-and-twenty-eight-and-both-predictions-about-why-were-wrong.md) |
| 55 | [Four hundred passages show he writes his own answer instead of copying](55-six-subjects-said-he-recites-and-four-hundred-say-he-composes-so-the-slice-was-aimed-at-the-wrong-behaviour.md) |
| 56 | [The official split overlaps documents: 14% of the eval leaked into training](56-the-official-split-guarantees-questions-not-documents-and-fourteen-per-cent-of-the-eval-was-in-the-slice.md) |
| 57 | [Extraction training works, mostly by declining answerable questions](57-the-slice-separates-on-all-three-rows-and-he-bought-it-by-declining-three-fifths-of-the-answerable-half.md) |
| 58 | [Tripling a fact type in training left his declines unchanged](58-the-corpus-was-not-the-prior-and-tripling-the-type-share-moved-it-by-nothing.md) |
| 59 | [No declines hide in unscored wording; the rest looks like salience](59-nothing-abstains-in-words-the-row-cannot-read-and-what-is-left-looks-like-saliency.md) |
| 60 | [Fine-tuning costs nothing but delivers three fifths of pretraining's gain](60-the-fine-tune-spends-nothing-and-delivers-three-fifths-so-the-mix-wins-on-efficiency-not-on-safety.md) |
| 61 | [The phrasing test itself has noise of sixty items](61-the-instrument-built-to-read-this-has-a-floor-of-sixty-and-four-seeds-made-every-floor-wider.md) |
| 62 | [The call grammar fixes 44% of bytes; the tokenizer blocks using it](62-the-grammar-knows-the-next-forty-four-per-cent-of-the-bytes-and-the-tokenizer-is-what-stops-it-saying-so.md) |
| 63 | [Fresh tool training, not new phrasings, fixed search routing](63-the-phrasings-were-never-the-problem-and-the-arm-without-them-fixed-all-twenty-five.md) |
| 64 | [Re-reading the prompt each round costs launches, not tokens: 0.22 ms](64-prefill-costs-launches-not-tokens-so-forty-two-per-cent-redundancy-was-worth-nought-point-two-milliseconds.md) |
| 65 | [Fine-tuning installs extraction at 260M from zero](65-extraction-installs-by-fine-tune-at-260m-and-the-sixth-findings-boundary-does-not-hold-here.md) |
| 66 | [The extractor takes the first value of the right type](66-the-extractor-takes-the-first-value-of-the-right-type-and-flipping-the-clause-flips-which-question-it-answers.md) |
| 67 | [The best tool-router never declines; the best decliner never serves](67-the-checkpoint-that-routes-best-never-declines-and-the-one-that-declines-best-never-serves.md) |
| 68 | [At 260M the seed barely moves scores, measured for the first time](68-the-seed-moves-nothing-on-the-frozen-rows-and-that-is-the-error-bar-every-260m-finding-has-been-missing.md) |
| 69 | [The tools data, not extraction data, displaced his declining](69-the-tools-corpus-displaced-decline-not-the-extraction-slice-and-the-see-saw-wobbles-by-fifty-five-turns-on-the-seed.md) |
| 70 | [The first-value rule holds on a new fixed test set](70-the-paired-property-row-exists-and-the-first-taker-rule-survives-being-put-on-a-frozen-file.md) |
| 71 | [Giving memory-lookup calls real results turns silence into recitation](71-finishing-the-chain-converts-silence-into-recitation-and-the-hard-zero-that-held-at-every-size-goes-to-twenty-six-of-twenty-six.md) |
| 72 | [Search returned 'capital punishment' for 'capital of Mongolia'; fixed](72-capital-of-mongolia-means-capital-punishment-until-the-sort-stops-helping-and-a-surname-counts-toward-its-whole-name.md) |
| 73 | [Training both answers on one phrasing breaks the serve/decline trade-off](73-the-see-saw-breaks-when-one-carrier-carries-both-answers-and-the-supply-lines-buy-the-serve-column-on-top.md) |
| 74 | [Second-turn behaviour installs; compound requests forget how to stop](74-the-second-turn-installs-on-both-vehicles-and-the-compound-one-buys-composition-by-forgetting-how-to-stop.md) |
| 75 | [Fine-tuning doesn't overwrite what pretraining installed](75-the-fine-tune-does-not-overwrite-what-the-mix-installed-and-the-re-ask-band-comes-back-whole.md) |
| 76 | [A single-request control removes the compound requests' copying cost](76-the-single-request-control-returns-the-copy-rows-on-both-vehicles-and-the-failure-species-is-the-controls-own.md) |
| 77 | [At 5B tokens, fresh text is no worse than re-reading text](77-the-fresh-strings-bet-holds-at-5b-and-the-one-row-down-fails-by-over-resolving-the-date.md) |
| 78 | [Forcing copied search queries breaks follow-ups; keyword shortcuts catch few chats](78-the-query-slot-buys-nothing-on-this-base-and-the-social-hatch-catches-five-in-thirty.md) |
| 79 | [A quarter of search results pass the relevance check on one letter](79-a-quarter-of-what-clears-the-coverage-bar-clears-it-on-a-first-letter-and-the-abstract-path-has-no-bar-at-all.md) |
| 80 | [Contradicting a trained behaviour needs that behaviour's data replayed](80-the-contradicted-class-needs-its-own-slice-back-and-five-arms-could-not-see-it.md) |
| 81 | [The answer score measures willingness to answer, not confidence](81-the-isolated-score-is-a-willingness-meter-and-every-read-time-route-to-the-span-is-now-closed.md) |
| 82 | [Scored fairly, the boundary model trails plain generation](82-the-repair-headroom-was-containment-and-the-only-rule-that-survives-its-control-buys-the-determiner.md) |
| 83 | [The boundary model finds answers but can't prefer them to silence](83-the-boundary-head-locates-the-span-and-cannot-prefer-it-to-the-null.md) |
| 84 | [A fallback rule buys 35 answers, but refusals still dominate](84-the-fallback-reduce-buys-thirty-five-right-answers-at-the-same-conditional-accuracy-and-the-refusal-still-owns-half-of-what-is-left.md) |
| 85 | [The checker needs cross-fitted labels; fallback rules are exhausted](85-the-verifier-label-has-to-be-cross-fitted-and-the-extent-rule-buys-eight-for-nothing.md) |
| 86 | [A checker that reads the candidate answer works; re-ranking does not](86-the-verifier-that-reads-the-span-it-verifies-clears-the-verifier-bar-and-the-re-ranker-cannot-choose-better-than-the-span-head.md) |
| 87 | [The passage reader ships: 389 of 721 right, up 107](87-the-reader-head-ships-and-the-runtime-reads-what-the-replay-said-it-would-to-the-passage.md) |
| 88 | [Social replies install by fine-tune; the fix moves failures elsewhere](88-the-social-class-installs-on-top-of-ft4g-the-family-repair-moves-the-failure-rather-than-removing-it-and-the-vague-tail-closes-by-a-line.md) |
| 89 | [Wrong rival answers are mostly about position on the shipped checker](89-the-rival-is-positional-on-the-shipped-verifier-and-the-plans-premise-holds-only-on-the-head-it-was-written-from.md) |
| 90 | [A nearby-words rule can't tell a rival answer from the right one](90-the-locality-rule-fires-on-correct-extractions-at-the-rate-it-fires-on-rivals-so-the-sixty-sixth-findings-runtime-repair-is-closed.md) |
| 91 | [The hard questions are those with nothing nameable in them](91-the-questions-he-fails-are-the-ones-with-nothing-nameable-in-them-and-constraint-carrying-questions-are-the-easy-half.md) |
| 92 | [Reading the whole passage tells the checker nothing new](92-the-passage-tells-the-verifier-nothing-the-window-has-not-already-said-and-the-arms-that-assume-otherwise-flip-sign-between-seeds.md) |
| 93 | [A perfect sentence finder would be worth only 15-38 passages](93-two-thirds-of-what-a-locator-could-reach-is-already-in-the-right-sentence-and-perfect-selection-from-the-heads-own-ten-caps-at-fifty-eight-per-cent.md) |
| 94 | [A 16-word hand-written lexicon matches the trained checker where it applies](94-a-sixteen-entry-hand-written-anchor-lexicon-ranks-windows-level-with-the-trained-verifier-where-it-speaks-and-misses-the-bar-because-it-is-silent-on-four-fifths.md) |
| 95 | [The right answer is among the top ten on 90% of misses](95-the-gold-is-among-the-heads-own-ten-on-nine-tenths-of-the-residue-so-the-fifty-eight-per-cent-ceiling-was-an-artefact-of-conditioning-on-admission.md) |
| 96 | [Given only the right window, the reader reaches 93%](96-admitting-only-the-golds-own-window-reads-ninety-three-per-cent-so-the-eighty-three-was-an-oracle-that-left-every-rival-in-the-vote.md) |
| 97 | [Fallback answer rules still don't help at the shipped setting](97-the-reduce-family-stays-closed-at-the-point-that-ships-and-the-hard-negatives-the-next-arm-wanted-are-already-more-than-half-its-training-nulls.md) |
| 98 | [A generated question frame invents relations more than a hand-written one](98-the-generated-frame-names-a-relation-the-question-never-carried-on-three-quarters-of-its-anchors-and-inverts-worse-than-the-hand-written-lexicon-so-the-frame-moved-the-confabulation-upstream.md) |
| 99 | [Ranking candidates together makes the checker worse on both seeds](99-the-listwise-verifier-fails-the-mechanism-bar-on-both-seeds-and-the-metric-it-was-selected-on-picks-the-wrong-arm-in-the-same-direction-twice.md) |
| 100 | [Two bidirectional layers over the reader add nothing](100-the-encoder-over-the-cached-states-gets-more-confident-and-no-more-right-so-the-pick-arm-fails-its-gate-below-the-head-it-was-meant-to-beat.md) |
| 101 | [Reading question fit improves refusals but not right answers](101-the-verifier-that-reads-the-windows-fit-to-the-question-buys-a-better-refusal-on-three-seeds-and-no-more-right-answers-so-the-arm-clears-both-floors-and-misses-the-bar.md) |
| 102 | [Twice the training epochs doesn't improve the answer finder](102-twelve-epochs-of-the-built-span-head-land-under-the-six-epoch-head-on-its-own-metric-so-the-budget-sentence-was-not-hiding-a-gain-and-the-epochs-lever-closes-at-the-gate.md) |
| 103 | [Averaging three seeds' readers barely helps](103-three-seed-heads-averaged-rank-the-gold-first-on-four-more-passages-while-any-one-of-them-being-right-would-be-sixty-one-more-so-the-pick-variance-is-real-and-averaging-cannot-harvest-it.md) |
| 104 | [Under the owner's rules, a fifth of 'wrong' answers are right](104-under-the-owners-rules-a-fifth-of-the-readers-wrong-answers-are-right-on-every-seed-so-the-lenient-column-reads-423-430-and-442-beside-the-strict-record.md) |
| 105 | [The answer-length rule is already at its best setting](105-the-extent-rule-is-at-its-optimum-and-neither-a-wider-tolerance-nor-a-wider-reach-buys-the-fuller-answer-the-owner-asked-for-while-dropping-the-article-costs-ten-right-answers-a-seed.md) |
| 106 | [Fifty thousand extra labelled windows don't help the reader](106-fifty-thousand-squad-windows-lift-the-span-head-on-one-seed-and-sink-it-on-the-other-and-move-the-population-a-pick-by-two-and-minus-five-so-more-labelled-windows-are-not-the-lever-either.md) |
| 107 | [Later layers know slightly more; the shipped checker already has it](107-the-say-marker-knows-more-about-the-pick-at-layer-eighteen-than-at-twelve-and-the-shipped-verifier-already-knows-all-of-it-so-a1-closes-at-its-cheap-read.md) |
| 108 | [The reader is sensitive to prompt wording, but no wording does better](108-the-states-are-not-prompt-invariant-yet-no-other-prompt-form-lands-the-gold-on-fifteen-per-cent-of-the-misses-so-a2-closes-on-its-go-bar.md) |
| 109 | [Other layer choices don't beat the shipped one](109-five-layer-bands-on-the-same-ten-thousand-windows-rank-the-shipped-band-at-the-top-within-a-point-so-the-picks-missing-signal-is-not-in-another-three-layers-of-the-stack.md) |
| 110 | [Of four cheap rescoring ideas, only one vote per mention helps](110-the-four-free-replays-the-audit-ranked-first-agreement-and-willingness-add-nothing-at-the-floor-per-bucket-thresholds-fit-the-folds-and-one-vote-per-occurrence-is-the-only-one-positive-twice.md) |
| 111 | [Overlapping windows add nothing; answers near a cut edge are missed](111-the-second-view-of-an-occurrence-is-right-on-a-quarter-of-the-misses-and-averaging-them-loses-ten-a-seed-while-a-gold-near-a-cut-edge-is-picked-ten-points-less-often.md) |
| 112 | [Training on whole passages lifts extraction from 54% to 71%](112-the-trunk-fine-tuned-on-whole-passages-reads-five-hundred-and-thirteen-and-five-hundred-and-ten-on-two-seeds-and-the-bidirectional-flip-without-adaptation-reads-under-the-frozen-reader.md) |
| 113 | [A checker on the whole-passage reader doesn't beat its own confidence](113-the-pair-rows-verifier-on-the-whole-passage-adapter-is-the-margins-own-curve-on-the-answerable-half-and-forty-silences-worse-on-the-other-so-it-closes-at-its-willingness-control.md) |
| 114 | [Tuning answer length on the new reader changes nothing](114-the-extent-rules-reach-and-tolerance-on-the-whole-passage-adapter-move-right-by-one-to-four-passages-inside-noise-on-both-seeds-so-clipped-is-not-bought-back-by-the-grid.md) |
| 115 | [A copy-check bug refused answers like 'best-of-seven'](115-the-grounding-rule-strips-frame-words-out-of-the-middle-of-a-span-before-testing-contiguity-and-on-the-whole-passage-adapter-that-refuses-ten-and-seven-right-answers-a-seed.md) |
| 116 | [A fix to the copy check lifts the whole-passage reader to 523](116-the-grounding-rule-now-tests-the-span-as-said-and-the-two-frozen-checkpoints-re-score-byte-identically-on-every-pass-count-while-the-adapter-reads-523-and-517.md) |
| 117 | [The whole-passage reader ships: 526 of 721 at runtime](117-the-whole-passage-adapter-reader-ships-and-the-runtime-reads-526-of-721-at-half-the-latency-with-the-three-passages-over-the-replay-traced-to-the-harvests-bf16-trunk.md) |
| 118 | [The reader survives the base model being fine-tuned underneath it](118-the-shipped-adapter-survives-the-trunk-moving-under-it-reading-521-and-524-of-721-on-two-social-trunks-against-526-on-its-own.md) |
| 119 | [Fine-tuning from the shipped base: frozen scores hold, small social costs](119-arm-two-s-payload-from-the-ft4g-init-lands-inside-arm-two-s-band-on-every-social-row-with-every-frozen-row-unmoved-and-the-init-s-cost-is-two-novel-declines-and-seven-social-moves-after-a-tool-turn.md) |
| 120 | [Consolation replies barely move and cost tool routing](120-the-consolation-family-moves-one-to-six-and-pays-six-on-each-half-of-the-routing-pair-through-its-own-balancing-class-and-the-rater-confirms-the-lexicon.md) |
| 121 | [Cutting mood-prefixed search calls removes the whole cost](121-with-the-mood-prefixed-calls-cut-the-routing-pair-returns-to-arm-four-and-the-consolation-row-holds-so-the-class-was-the-whole-cost.md) |
| 122 | [The second social turn installs and lifts the first](122-the-second-social-turn-installs-and-lifts-the-first-declared-abstention-reads-111-of-112-nothing-reissues-and-the-one-cost-is-a-routed-say-that-speaks-a-life-on-questions-about-his.md) |
| 123 | [One unrelated exchange in history stops repeated calls](123-with-one-unrelated-exchange-in-front-of-the-bound-pair-nothing-reissues-at-depth-three-copied-from-reads-none-on-all-seventy-two-and-novel-decline-returns-to-thirty-two-of-thirty-two.md) |
| 124 | [Refitting the reader on the social model reads 517 at runtime](124-the-reader-is-re-fit-on-the-social8-trunk-and-reads-514-on-the-harvest-and-517-at-runtime-nine-under-the-ft4g-adapter-read-on-the-same-trunk-and-the-pair-ships.md) |
| 125 | [Two decisions: whole-passage reader by default, life questions declined](125-decisions-seven-and-eight-are-taken-the-whole-passage-reader-is-the-default-and-a-routed-question-about-his-life-is-answered-by-a-decline-that-says-he-is-a-model.md) |
| 126 | [A hand-driven session found a chat turn sent out as a search](126-a-hand-sitting-under-all-found-the-two-history-rows-that-read-zero-and-the-leak-that-sends-a-private-sentence-to-a-provider-and-three-runtime-fixes-move-no-row-of-the-release-triple.md) |
| 127 | [Two thirds of one dataset's tool calls were invalid JSON](127-a-spurious-memorisable-slot-was-the-copy-audit-going-blind-on-escaped-quotes-and-underneath-it-two-thirds-of-the-relpairs-calls-are-invalid-json.md) |
| 128 | [Questions about his life go to the web six times in ten](128-a-life-question-goes-to-the-web-six-times-in-ten-the-fold-and-the-reserve-move-no-copy-column-and-the-first-distractor-copy-is-seen-at-depth-three.md) |
| 129 | [He learns to label his own request; forcing labels doesn't change calls](129-the-parse-installs-and-half-of-it-is-label-content-and-none-of-it-reaches-the-calls-on-two-corpora-four-arms-and-two-hundred-and-forty-forced-tags.md) |
| 130 | [A label in the text is a hint, never the decision](130-the-tag-in-the-stream-is-read-as-a-prior-and-never-as-the-decision-zero-of-seven-hundred-and-twenty-forged-maps-at-two-layers-with-and-without-the-request-under-loss.md) |
| 131 | [Once the runtime enforces the label, a forged one is obeyed 36/36](131-the-tag-becomes-the-door-and-the-door-is-the-runtimes-the-role-grammar-alone-takes-the-tree-from-eighteen-to-forty-five-of-sixty-on-an-unmasked-checkpoint-and-the-mask-adds-nothing.md) |
| 132 | [Rotary position embeddings beat learned positions on most tests](132-rope-against-learned-positions-on-the-dummy-world-above-on-the-trained-parse-at-both-seeds-three-per-cent-better-on-the-language-rows-two-below-on-the-bound-tree-and-the-held-out-rows-zero-as-ever.md) |
| 133 | [On a synthetic world he generalises labels but not one level deeper](133-on-a-world-where-the-phrasing-is-useless-for-the-label-he-cuts-phrasings-he-never-saw-at-every-seed-repairs-a-wrong-label-after-it-fails-and-still-writes-nothing-one-level-deeper-than-he-was-shown.md) |
| 134 | [He learns to write a summary line of conversation state](134-he-learns-to-write-the-state-line-at-nano-a-merely-present-line-moves-the-repeat-only-on-the-cells-trained-on-it-and-the-first-scoring-read-zero-because-the-prompt-ended-on-a-space.md) |
| 135 | [More depth-3 training data doesn't teach depth 4](135-raising-the-depth-3-share-at-saturated-shape-coverage-deepens-the-depths-shown-and-leaves-the-unseen-depth-at-the-floor-exposure-is-not-the-lever.md) |
| 136 | [The depth-4 failure is a position never seen, not missing recursion](136-the-depth-4-zero-is-a-position-the-corpus-pinned-at-zero-he-predicts-the-fourth-level-and-will-not-open-the-span.md) |
| 137 | [The depth-3 failure doesn't track copy length](137-the-level-3-floor-is-flat-against-every-covariate-that-moves-the-trained-levels-copy-burden-is-not-what-pins-it.md) |
| 138 | [He knows where the next request part starts, 80 to 93 percent](138-the-level-1-cursor-is-in-the-weights-at-eight-in-ten-interior-boundaries-and-no-line-that-loses-it-passes.md) |
| 139 | [Aligning training blocks to transcript starts helps parsing, short of target](139-arm-a-at-one-seed-aligned-blocks-move-the-cursor-and-cut-invented-spans-by-a-fifth-and-put-the-copy-band-under-its-kill-line.md) |
| 140 | [Depth-4 failure is position alone; moved to line one it works](140-the-depth-4-zero-is-a-position-and-nothing-else-the-identical-cut-reads-seventy-one-to-eighty-nine-of-ninety-five-at-line-1.md) |
| 141 | [Written as one nested line, he builds a structure never trained](141-he-writes-a-nesting-the-corpus-never-contains-eighteen-times-across-two-seeds-and-nearly-six-times-more-often-when-called-for.md) |
| 142 | [Removing four-member groups from training broke nesting another way](142-arm-g-took-its-four-member-groups-out-of-the-pairs-and-he-stopped-reading-an-unmarked-pair-as-a-group-so-its-null-on-nested-four-is-confounded.md) |
| 143 | [Nesting at 20M breaks two different ways; too fragile to build on](143-arm-g2-held-every-pair-and-the-trained-nesting-fell-anyway-he-flattens-the-nested-pair-into-the-outer-group-so-nesting-at-nano-is-too-fragile-to-carry-the-ladder.md) |
| 144 | [Showing the request step by step fixes short chains, not long ones](144-arm-s-stepwise-views-land-in-the-null-band-at-both-seeds-they-train-the-short-chain-and-cure-the-social-misread-and-not-the-nested-open-which-they-teach-78-times.md) |
| 145 | [The depth limit is the linking word; re-showing uncovered text fixes it](145-the-depth-wall-under-the-windowed-runtime-is-the-carrier-word-and-re-presenting-the-uncovered-gap-takes-arm-s-to-095-and-089.md) |
| 146 | [A runtime gap-filling rule breaks nothing but fixes little on real requests](146-the-gap-rule-breaks-nothing-on-fresh-requests-and-fixes-almost-nothing-every-firing-on-a-right-parse-is-read-back-as-a-connective-and-natural-text-rarely-holds-the-flat-carrier.md) |
| 147 | [When the runtime holds the structure, invented words vanish; grouping stays his](147-the-bind-owns-form-and-the-copy-pointer-not-the-count-a-marked-chain-passes-the-depth-wall-and-he-skips-words-instead-of-inventing.md) |
| 148 | [Picking a template by letter never installed; one seed in three learned](148-the-letter-first-pick-never-installed-and-evidence-first-reads-the-wish-on-one-seed-of-three-so-rung-3-is-a-direction-not-the-kill.md) |
| 149 | [With checkable rules filtered, he picks the template matching the request](149-split-like-rung-3-he-picks-the-template-whose-soft-clause-answers-the-wish-and-follows-it-when-swapped-accept-or-none-never-installed.md) |
| 150 | [On real requests the runtime's machinery works but his own parse doesn't](150-on-real-carriers-the-door-works-and-his-cut-does-not-and-the-one-real-cost-is-a-chat-label-read-off-the-tools-header.md) |
| 151 | [Ignoring groups he closes too early lets the interpreter pass](151-the-windowed-interpreter-passes-g1-once-a-close-he-writes-early-in-a-cut-view-is-not-believed.md) |
| 152 | [What each layer of the tag language costs in tokens](152-what-each-layer-costs-the-render-pass-layers-add-a-fifth-of-a-turn-and-the-conversational-slice-has-no-turn-in-it.md) |
| 153 | [He writes a summary of the conversation state but doesn't use it](153-the-state-lines-second-seed-he-writes-it-again-and-the-repeat-does-not-fall-under-it-the-record-is-written-and-not-read.md) |
| 154 | [With no template he completes nothing; inside one, every task runs](154-g5-unseen-templates-run-where-he-cannot-compose-alone-and-his-judgment-rides-into-a-composition-unchanged-selection-is-chance.md) |
| 155 | [A new fine-tune recipe keeps follow-ups but 'what about X?' still fails](155-the-4j-recipe-at-its-second-seed-holds-the-chain-family-where-ft4-loses-it-at-both-and-the-held-out-carrier-stays-zero-at-both.md) |
| 156 | [He can't build a goal from two observations at one pass](156-g6-combine-does-not-install-at-one-pass-he-copies-a-clause-from-the-note-and-the-request-never-chooses-which.md) |
| 157 | [Writing his move first steers the reply and beats the old regex](157-a3-the-move-line-steers-the-reply-at-both-seeds-and-installs-on-trained-phrasings-split-by-the-thinnest-family-unseen-phrasings-default-to-one-value.md) |
| 158 | [Wordings seen over ten times get memorised; key phrases become lists](158-memorise-or-learn-is-readable-off-the-data-wordings-seen-more-than-ten-times-are-labelled-from-memory-and-a-settled-carrier-is-learned-as-a-list.md) |
| 159 | [More ways to phrase each move helps unseen phrasings modestly](159-a3b-lifts-unseen-phrasings-at-both-seeds-and-capping-repetition-buys-nothing-on-far-phrasings-finding-158s-lever-is-not-shown-at-nano.md) |
| 160 | [2048-token blocks cost 1.2x training time and fit in memory](160-the-blocks-costs-2048-trains-at-1-2x-fits-a-fine-tune-in-the-same-memory-decodes-free-on-a-short-turn-and-slow-deep-in-a-full-window.md) |
| 161 | [His internal state knows more than he writes about move choice](161-inside-him-the-move-is-in-his-state-at-the-word-counters-level-in-every-arm-and-the-arms-differ-in-how-much-of-it-the-label-uses.md) |
| 162 | [Real dialogue openings replaced the hand-written ones rather than adding to them](162-the-real-arm-reads-unreadable-the-soda-deck-displaced-the-hand-written-consolation-carriers-and-the-state-on-far-phrasings-is-level.md) |
| 163 | [Capping real openings at half keeps both consolation styles; greetings drop](163-the-mix-arm-reads-real-only-by-its-table-it-holds-both-kinds-of-consolation-and-loses-greeting-with-the-evidence-level.md) |
| 164 | [Greeting accuracy swings eight items on identical data](164-the-mix-arms-second-draw-greeting-is-unreadable-and-both-kinds-of-consolation-hold-on-every-mix-checkpoint.md) |
| 165 | [The cap costs greetings in what he writes, not what he knows](165-the-cap-costs-greeting-in-what-he-writes-and-not-in-what-he-holds.md) |
| 166 | [Halving the tool data leaves tool use intact](166-the-tool-share-at-half-the-call-surface-holds-under-the-door-and-the-one-cost-is-the-refusal-relay-cutting-the-copied-query-short.md) |
| 167 | [He can't learn which limit a person will relax](167-g6-recover-does-not-install-at-one-pass-he-relaxes-by-a-fixed-ranking-of-the-fields-and-the-persons-words-never-reach-the-choice.md) |
| 168 | [Naming the flexible limit outright splits the seeds](168-recover-with-the-field-named-outright-seeds-split-both-learn-whether-the-person-bent-one-learns-which-limit-and-the-copy-kill-fires.md) |
| 169 | [Choosing a branch from a checked condition: seeds split](169-branch-installs-at-one-seed-of-two-every-trained-wording-at-2337-none-at-1337-no-new-wording-at-either-and-the-copy-kill-fires-at-both.md) |
| 170 | [The copy test's failure threshold was measuring seed noise](170-the-copy-bands-standing-kill-measured-seed-noise-seeds-of-one-arm-spread-up-to-54-items-and-the-band-was-3-to-4.md) |
| 171 | [At 50M, branch choice still splits across seeds](171-branch-at-50m-splits-again-the-other-way-two-runs-of-four-install-at-20m-and-50m-so-size-to-50m-does-not-steady-the-binding.md) |
| 172 | [The starting model, not the trace format, makes branching reliable](172-the-worker-frame-does-not-steady-branch-the-starting-model-does-e2-starts-install-11-of-12-across-four-forms-and-v-starts-4-of-12.md) |
| 173 | [Branch choice falls to chance when condition words flip the meaning](173-branch-with-flip-words-takes-away-the-table-and-nothing-forms-in-its-place-chance-on-its-own-training-traces-and-a-fixed-taste-in-place-phrases.md) |
| 174 | [A space after the bracket shifts his default to the first option](174-a-space-after-the-menu-bracket-moves-his-default-from-a-taste-in-phrases-to-the-first-option-and-the-binding-still-does-not-form.md) |
| 175 | [He names the chosen branch, but can't combine it with the result](175-his-binding-line-installs-he-reads-the-flip-words-beside-the-request-on-92-to-99-percent-and-the-pick-reads-the-line-but-crossing-it-with-the-result-does-not-form.md) |
| 176 | [Naming both branches fixes the pick but blurs 'not'](176-the-two-branch-binding-line-closes-the-pick-every-quad-right-on-a-right-line-and-a-forged-line-followed-576-of-576-and-the-gate-passes-on-all-three-the-line-is-the-wall-now.md) |
| 177 | [Leaving the second slot out of training doesn't restore 'not'](177-the-runtimes-else-slot-does-not-bring-the-negation-read-back-the-first-slot-stays-at-0-68-and-the-one-slot-lines-0-94-is-the-best-binding-on-record.md) |
| 178 | [Naming a second branch blinds him to 'not'](178-a-second-slot-in-the-binding-line-blinds-him-to-not-structural-at-both-seeds-from-the-slot-itself-with-or-without-the-pick-while-unless-survives.md) |
| 179 | [Fine-tuned, he reads every condition word like 'not' and 'unless'](179-by-fine-tune-the-one-slot-line-reads-every-flip-word-with-the-pick-out-of-his-loss-the-complement-never-forms-and-real-sentences-in-new-structures-fail.md) |
| 180 | [When the runtime orders the menu, 'the other one' is perfect](180-with-the-runtime-writing-the-menu-in-his-lines-order-branch-is-his-pick-and-both-halves-excel-the-other-one-864-of-864-and-own-quads-141-to-144-at-three-starts.md) |

Design decisions that are not findings live in
[DESIGN-NOTES.md](../DESIGN-NOTES.md). Results from *outside* this project — read but
not replicated, and therefore not findings either — live in
[EXTERNAL-RESEARCH.md](../EXTERNAL-RESEARCH.md).

## The story so far

There is also, as of the eval harness below, a fixed ruler to measure the next few
experiments against — which every remaining Phase 1 step needs, because all of them are
comparisons across corpora. Both comparisons it was built for have now run. The fifth finding
is the pilot mix: a 25M model with the tool format in pretraining routes to the tool
essentially always, where the same model without it never does. The sixth is the control arm,
and it is the more interesting one — a fine-tune installs the format just as well, and still
cannot be made to use the tool's answer instead of its own. The seventh is the first run on
text nobody in this project manufactured: 199M tokens of filtered web, and the result that
survives it unchanged is precisely the one the sixth rests on. The eighth is not a training
run at all — it is the tokenizer measurement §2 has been waiting on a real corpus for, and it
retires the last argument for staying at byte level. The ninth spends it: the same text at
BPE 8k is better on every language-modelling row in a third of the wall clock, and about a
fifth of that turns out to be context rather than tokenization. The tenth builds the tool
slice the harness has been missing rows for since it was written, and finds that what a
generator cannot manufacture is not correctness but variety. The eleventh prices that
shortfall: a 25th of the share §4 declared buys most of the tool behaviour for free, and
buying the rest by repetition improves which tool he picks while breaking how he calls it.
The twelfth asks the question the slice was built for and gets the uncomfortable answer —
the copy discipline every earlier conclusion rests on does not reach a second tool, because
that tool's answers were drawn from a table small enough to memorise. The thirteenth acts on
that diagnosis: replacing the table with an invented world of 8,700 facts takes the row from
27/120 to 120/120 without touching the model, and discharges a caveat that had stood since the
sixth finding. The fourteenth builds the structured slice, hits the identical bug a third time
in a corpus written the day after learning it, and turns three incidents into one rule — any
span the model must copy has to come from a space too large to memorise as a set. The
fifteenth prices that slice and finds §4's 10% is four times too big: a quarter of it keeps
89% of the gain and hands the tool rows back, giving the first checkpoint that is best on
every row at once. The sixteenth builds the tenth eval row — the one that can see a model
repeating itself, which the other nine cannot — then cuts children's stories from 47% of the
corpus to 10% and finds it buys the largest language-modelling gain in the project and moves
output variety by 0.1 of a point. The seventeenth is the one that reaches backwards: a second seed on
an unchanged corpus moves the row nobody thought moved by eighteen items, and puts every
generation-scored delta in this document under suspicion. The eighteenth finds the cause — that
row asks six questions in a hundred and twenty costumes, so everything ever read off it was a
whole number of facts — and the rule that would have caught it had been written eight days
earlier and pointed only at the corpus. The nineteenth spends four seeds measuring what each
row's noise actually is, and the answer is that they do not share one: a ten-item move is
overwhelming on one row and invisible on another, and the project had been reading both the
same way. The twentieth turns that instrument on the back catalogue and finds copy discipline
has never been shown to depend on the corpus at all. The twenty-first explains why — it is a
step function on the tool slice *existing*, 0/300 without it and flat across a 25x range of
shares above it — and the control half is the better half, because a slice teaching perfect
deference on one tool carries none of it to another. The twenty-second is the first arm where
everything that sounded right failed the ruler. The twenty-third kills a screen the project had
trusted for weeks: §5.0's lexical bar correlates −0.976 with web share and −0.045 with the thing
it was supposed to predict, so it was measuring the corpus it was applied to. The twenty-fourth
buys the slice that bar had rejected, and it costs prose and nothing else. The twenty-fifth
builds a register row, which the project had never had, and finds the conversational slice takes
dialogue register from 23% to 76%. The twenty-sixth withdraws the twenty-fifth's other half: the
median turn it rested on was pooled across two prompt sources and described neither, and there
was never a shape gap. The twenty-seventh is the first corpus that inherited nothing, and its
result is a row moving 2.5 points while its own slice stays byte-identical — so the row prices
the mix, not the slice. The twenty-eighth tests the oldest caveat in the document, that the
behaviour rows were only ever scored on phrasings the generators wrote, and splits the harness
in two: routing collapses on wording no generator emits, deference does not move by one item,
and the whole of the difference is the single token sitting to the left of the span. The
twenty-ninth spends that diagnosis on the first arm this project has run against a mechanism
rather than a share, and a seed replicate turns the answer clean: widening those left edges
from six to twenty-four takes the edges it contains to a perfect score twice over and transfers
nothing at all to the edges it does not, so a span's boundary is a memorisable set exactly like
its contents. The thirtieth is what those four seeds cost to find out and what they priced on
the way: a row's noise floor is a property of the arm it is scored on rather than of the row,
the same row moves 3, 22 and 45 items across three arms of one checkpoint set, and every floor
this document quotes was measured in the one regime where a floor matters least. Replicating the
baseline as well then retires the floor entirely for this comparison: eight checkpoints, and the
two ranges either overlap or they do not. Read back over the catalogue it costs the nineteenth
finding both of the results it *added* rather than removed — the regression it un-dismissed and
the unreadability rule it demolished — and the ~35 it discarded turns out to sit between the two
families measured since. The thirty-first brackets the twenty-ninth's intervention and finds no
knee to find: twelve left edges buy the carriers they cover as completely as twenty-four do, and
because a handful of left edges are simply common in English, half the templates carry 86% of
the items, so the fix was already cheap. The bucket that was meant to test whether any of it
generalises turns out to be twelve items whose *untreated* range touches its own ceiling, which
answers nothing at any seed count. The thirty-fifth counts what the corpus actually shows him and
finds the answer is one per cent: every marked-up transcript in the project calls a tool except
a thousand of ninety-nine thousand, while the twenty per cent of the budget that makes him
conversational carries no markers at all, so dialogue and `<|user|>` were learned in disjoint
universes. Giving him the missing class — real dialogue, marked up, no call, at 1.19 uses per
reply — moves abstention on uncovered requests off a floor every checkpoint in the project sat
on, lengthens his replies to the corpus's own median, and does not make them more varied, which
is the first time getting the cardinality right has failed to move the row it was aimed at. The
quantity was never unmeasured: `called_anyway` sat in every scorecard reading 13 to 19 of 19,
pooled into `tool.selection` so that the best tool model in the project reads 181/200 with
eighteen of its nineteen failures being one behaviour. And the row built to unpool it arrives
with its own ceiling on the half made of real sentences, which is the thirty-first finding's
complaint committed by the file written to prevent it. The thirty-sixth closes the confound the
`turn2_reply` handoff left open rather than resolved. Replies after a conversational preamble are
longer than after a tool one, and pooled distinct-3 is not independent of length, so "register
carries across the turn" and "he just says more" both fit the published table. Matching the two
cells on their exact length histogram — identical pool sizes, so neither the type/token effect nor
the canned-short-reply effect can act — leaves the gap positive on four checkpoints of four, with
a draw interval that never crosses zero. The confound was real and worth 0.005 to 0.015 of a gap
around 0.05. Two things fall out on the way: the 200 utterances are disjoint between the cells, so
the raw column was partly an item-set difference, and the control for that was `first_by_preamble`
sitting unused in the harness — length-matched and with no preamble in front of either cell, the
`talk` items carry no advantage at all, and two of four run negative. The gap appears exactly when
the preamble does. What none of it buys is a size: not one of the four controls clears the seed
spread that produced it, so the direction is settled on four checkpoints and the magnitude is
still unpriced. The thirty-seventh spends that instrument on the arm it was
built for and gets a negative with a bill attached. `chat2.txt` — the two-turn no-call class the
corpus never had — goes in at a 25th of one pass, and `called_anyway` on the nineteen
out-of-scope items of `turn2.second` reads **19 of 19 in all four cells, both sides**: the class
was added in exactly the position it was missing from and the behaviour it targets did not move
by one item. Turn-1 abstention moved on a 5% slice in the thirty-fifth; turn-2 abstention does
not move on a slice in the same structural position, so the two are not one behaviour. What did
move is the thing nobody was buying: `turn2.second` falls from [166, 168] to [147, 149], a
margin of 17 against within-arm spreads of 2, and the failure mass is wrong-tool rather than
over-abstention — which is checkable only because declining an item that wants a call scores
`unparseable`, and that bucket moves by three. The register gap narrows decisively at an
identical length histogram, and that cell is readable only because the thirty-sixth finding
established the gap survives length matching at all — the arm's median reply after a tool
preamble drops from 11 words to 8, so the raw cells would have been quoting length.

 The fifty-fifth asks the extraction question at a denominator that can refute an
answer for the first time, and it refutes the premise the plan was written on. Three rows cut
from Natural Questions dev — real queries, un-primed, issued before anyone saw the passage —
score a frozen `corn_jr_260m` at 9/200, 0/200 and 133/400, with 27 of 27 pre-existing rows
reproducing identically. `PLAN-WEB-SEARCH.md` had specified the slice from six hand-picked
subjects whose reading was that the substrate is faithful recitation and the job is to teach him
to copy *less*. Over 400 real windows, 18 of 400 replies are copies, 69 never become a sentence
at all — they reopen the JSON payload they were standing after — and 220 are window-length prose
he wrote himself at a median copied fraction of 0.09. The window says "19-year-old Jourdan
Miller" and he answers "21-year-old Jourdan Miller", which is not copying with an error but
composing over a topic. So the job is to teach him to copy at all, and the class mix was
rebalanced before a byte of the slice was generated. The first scorer hid the whole thing by
naming its length bucket `recited` — the answer it expected — which is the twenty-third finding's
shape on a bucket rather than a bar, and split honestly the same replies read 10 against 99. The
main row ships as an upper bound after three tightenings were tried and rejected: `grounded`
drops eight of twelve passes and three of the drops are correct extractions, copied fraction
scores the worst junk at 0.93 and a correct answer at 0.27, and a length bound fitted to twelve
observations is a ruler shaped by the sample it was read off. What it cannot say is anything
about a trained model, which is the point — nothing in the corpus has ever put a paragraph inside
an `<|obs|>`, and the external anchor that reads 100% failure at this size tested
instruction-tuned models and ran no fine-tuning at all.

 The sixtieth is the vehicle experiment, and it retires the sixth finding's
authority over Phase 3's shape without contradicting a number in it. P3-A hands both arms the
same 45MB of real dialogue cut from the middle of `conversational.txt` — text no trained
checkpoint has read, proved by tokenizing the 120M-byte prefix and measuring 32,463,975 tokens
against the 19,640,157 `mix_v3` draws — and holds expected payload exposure equal to 0.053%
across a pretraining arm and a fine-tune arm. Both controls were re-scored rather than
retrained and 121 of 121 shared quantities reproduced identically on each. Both arms deliver on
`lm conversational`; **neither spends a copy row**, and the fine-tune sits at the ceiling on
`tool.copy` while holding `temporal.copy` at 353/353 and losing no prose. Finding 6's fine-tune
lost both, and the difference is the three hardnesses removed together — a trained base rather
than a TinyStories one, a register payload rather than a capability, and replay of the whole
mix rather than narrative alone. So deference does not fine-tune *in*, and that is not the same
claim as deference being spent when phrasing is fine-tuned *over* it. What the mix wins on is
efficiency: the fine-tune buys 61% of the delivery at equal payload exposure, separating above
the mix by twice the spread. The run also puts a number on how finely one of the three standing
regression rows can be read — `tool.copy` moved nine of 120 items across five training
iterations of a single run, in the opposite direction to `tool.copy_wide`, while every
likelihood row moved in the fourth decimal — so the cost side is a null rather than a ranking,
and it has to be. Its own decision table then turns out to be silent on the thing the
experiment was supposed to gate: outcome 3 says the mix is favoured on efficiency, which is a
preference and not an ordering constraint, so whether P3-B's sentences must exist before the 5B
corpus is frozen is now a choice somebody has to state rather than a result anyone can quote.

## 80. The class installs every time, and what buys back the class it contradicts is that class's own slice

Entry 4's payload — a bare unmarked question after a lookup turn, **0 of 849** in the corpus —
trained seven arms over six configurations on `corn_jr_260m_v4`. **Every arm installed the class
completely and every arm was discarded.** Finding 74's 4x fine-tune discount was pre-registered
as the expected shape and appeared on none of them: `historygrid`'s defective cells go to
ceiling everywhere (attribute after a lookup 2/8 → 8/8, arithmetic 0/4 → 4/4, the pack arm 0/8 →
8/8, 6b's wrote-when-not-asked 4/4 → 0/4). Finding 75 survives too — `tool.copy` 120/120,
`tool.copy_wide` 300/300, `temporal.copy` 353/353 on every checkpoint of every arm. **What a
fine-tune of this base spends is routing priors**, and `chain_pronoun`'s failure mode moving
from `wrong_message` to `wrong_tool` is that in one number. Arm 1 starved the class its payload
contradicts 715:1 and took `chain_ellipsis` 49/50 → **7/50**; the separating arm — arm 1 to the
token with only `turn2` and `compound_v2` raised from 0.070% to 1.684% of the arm — brings it
back to **45/50 with the payload byte-identical**. So the rule is per-class and it is not a
general replay floor: **when a payload teaches a class that contradicts a trained one, the
contradicted class's own slice has to come back up in the replay.** Two claims made earlier in
this document are corrected inside it rather than removed, and the pattern in both was the same
— the matched-pair payload and the `turn2` boost always arrived together across five arms, so
the recovery was credited to the payload; a replay-share sweep then measured `tools`, a slice
carrying nothing the payload contradicts, and concluded no floor existed. `tool.name_fidelity`
is separately ruled out as a replay effect — 114/120 at `tools` 0.274% against 106/120 at
0.293% — and tracks the payload instead, worsening monotonically with the number of chain twins
in it. Left unexplained: `turn2.reask` is a no-call class like `react` and went *up* on every
arm while `react` never reached its ceiling.
