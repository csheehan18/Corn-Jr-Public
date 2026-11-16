# People asking an assistant fits the owner best; the answers do not

**Full result:** After the owner kept Apache 2.0 for the weights and left the non-commercial EmpatheticDialogues out (2026-10-22), two permissively licensed real-dialogue sources were read the same way as finding 210. OpenAssistant OASST1 (Apache 2.0, human-written; English: 15,979 prompts and 25,326 replies, 3.6M words) fits the owner's own typed messages best of any source read -- bigram perplexity 426 against Taskmaster's 648, EmpatheticDialogues' 718 and SODA's 938 -- because its prompts are people asking an assistant things, which is how he writes to Corn-Jr. Its replies are the problem: median 93 words, list-heavy and encyclopedic, some in a model's voice ("As a language model AI..."), one confidently wrong. Google's Taskmaster (CC BY 4.0, verified in the official README) is short task talk ("I need a seafood place.", "Make it a medium.") but narrow and the most formulaic source read (perplexity 55 on its own held-out messages, under SODA's 86)

**Cost:** licence checks, downloads (34 MB, 66 MB, 37 MB, 21 MB to `F:/corn-jr-data/convcand/`), the read (`scripts/probe_conv_sources.py`, `scripts/probe_owner_register.py`) and the hand read of 40 pairs, 16:12-16:30 on 2026-10-22. No card. ETA 30 min, actual ~18.

**The question** (owner, 2026-10-22: route (a) -- keep Apache, leave ED out;
find a permissive source). Finding 210: the owner writes to Corn-Jr as to an
assistant -- 69 messages, median 6 words, 0.38 short, 0.38 questions, 0.06
first person (counts only).

**Licences.** OASST1: Apache 2.0 on the HF dataset card, no message flagged
synthetic in the ready set. Taskmaster: "made available under the Creative
Commons Attribution 4.0 License" -- Google's README, the same terms as SODA.
PersonaChat: no licence found, not read.

## The read (`evals/results/conv_sources__read2.txt`)

    source   pairs     median words   <=4 words   question   first person   ppl stand-in   ppl own   ppl owner (69, counts only)
    soda     408,399   16             0.03        0.31       0.66           180            86        938
    ed       58,829    14             0.04        0.21       0.66           142            171       718
    oasst    25,243    15             0.04        0.67       0.41           427            186       426
    tm       352,784   8              0.21        0.34       0.32           379            55        648
    (pec 1,099, subs 954, dclm 1,386 on the owner's messages, finding 210)

## Read by hand (20 pairs each)

* **OASST prompts** are the owner's register: questions and requests to an
  assistant, typos kept ("What isbthe best programing language for 2023",
  "How can i Build myself", "Can I make it bigger?").
* **OASST replies** are another thing: median 93 words (37% are 60 or
  fewer), numbered lists, encyclopedic answers on chemistry, git and
  relativity, a model's voice in places, and a confident wrong fact (Satoshi
  Nakamoto as the century's most influential mathematician). Trained on, they
  teach reciting knowledge -- against the north star (navigate, not know)
  and Corn-Jr's short replies.
* **Taskmaster** is short, real-sounding task talk -- bookings, orders, car
  repair -- with a fifth of its messages four words or fewer, but its
  domains are few and its phrasing repeats.

## What it licenses

* **OASST's prompt side is the closest text to the owner's own messages in
  any source read**, under a licence the weights can carry. How to use it
  without its answers' habits is the open question: threads whose replies
  are short (37% of replies), or the prompts with replies he would write.
* **Taskmaster at most as a small share**, for short requests, under a cap:
  its repetition is a shortcut risk.
* **A 5M arm is the next read**, pre-registered like finding 211, on the
  same register gate (the owner's messages, counts only).

**What it does not settle.** Whether short-reply OASST threads move his
register; any size above 5M; the owner's register beyond 69 messages.
