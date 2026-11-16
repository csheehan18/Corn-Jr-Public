# His surprise spots unusual words, not words he misunderstands

**Full result:** On the shipped 260M, the summed surprise of each word of a request picks out the one hard word or phrase in it 28 of 40 times (single words 25 of 32, idioms 3 of 8), separates hard words from ordinary content words at AUC 0.873, and at the threshold that flags 75% of the hard words fires on 0 of 16 plain requests and on every name (8 of 8) and typo (8 of 8); it is no higher where he gets the meaning wrong (AUC 0.530), and a plain count of how often each word appears in his web text does better (33 of 40, AUC 0.918)

**Cost:** writing `scripts/probe_surprise.py` and its 72 requests 20:50-20:52 on 2026-10-20 (7ceb20b); the read on three checkpoints 28.9 s and twelve hand decodes 7.3 s, both contended (the card at 38-39%, a bound).

**The question** (owner, 2026-10-20). The design under discussion for 1.x:
when a request carries a word he does not know, he asks the person once
("what do you mean by *spendy*?"), the answer goes in a per-instance
glossary, and the runtime shows it beside the word every later time, so
nobody answers the same question twice. The runtime cannot judge
understanding. Can his own surprise -- the probability he gives each word
of the person's message, free from the prefill -- say which word to ask
about? "Let's do the surprise check first to get a sense of when he
doesn't know."

**The probe** (registered at 7ceb20b with its prediction). Hand-written,
nothing from any log: 40 requests each carrying one hard word or phrase --
12 slang, 9 regional, 11 rare, 8 idioms -- with a 4-way meaning check; 16
plain requests; 8 with a name or place; 8 with a typo. Per word, the summed
NLL of its tokens after `<|user|>`; a phrase is one unit at its most
surprising word; the first word of a message is left out.

## The read

    checkpoint                  hit@1   single  idiom   AUC     alarms: plain / names / typos   meaning AUC
    corn_jr_260m_v4_ft_social8  28/40   25/32   3/8     0.873   0/16 / 8/8 / 8/8                0.530
    corn_jr_260m_v4             30/40   26/32   4/8     0.872   0/16 / 7/8 / 8/8                0.393
    nano20m_v3                  37/40   29/32   8/8     0.944   1/16 / 6/8 / 8/8                0.427
    word count in his web text  33/40   --      --      0.918

**Against the prediction**: single words 0.78 against 0.55-0.75, idioms
0.38 against 0.10-0.30 (both above); AUC inside 0.80-0.90; plain requests
0 against 10-25% (better); names and typos all fire (held); meaning AUC
0.53 against 0.55-0.65 -- no relation at all; frequency at least as good
(held, and more).

**What it finds and what it misses.** It finds the word that looks
unusual: *bougie* 33.0 nats, *knackered* 34.2, *brekkie* 41.2, *FOMO* 27.5.
It misses the hard word that looks ordinary -- *lit* 8.1, *sus* 8.2, *grub*
14.9 (below *late*), *ubiquitous* 7.1 (below *e-scooters*) -- and the idiom
made of common words: *break the bank* 3.7, *hit the hay*, *a stone's
throw*. The 20M flags every idiom, where the 260M flags three of eight.

**Surprise is not understanding.** The meaning check says he picks the
right meaning of 18 of the 40; surprise is no higher on the 22 he misses.
And the check flatters him: twelve free decodes ('Q: In "...", what does
"X" mean? A: It means') answer none of them correctly -- *spendy* "that
you are willing to spend money on", *dodgy* "that the brakes feel heavy",
*on the cards* "that the card is for tomorrow", and the rest echo the
word or the request back. Of these 40, he understands close to none, so what surprise
separates here is **unusual against ordinary**, not **known against
unknown**.

## What it licenses

* **A trigger, not a judge.** Surprise says "this word is unusual", never
  fires on a plain request here, and is free: good enough to decide when
  to ask, at one question a message.
* **It needs two filters before it can ask.** Every name and every typo
  fires. A name is not a question to ask (the people store and
  capitalisation catch most); a typo is a different question ("did you
  mean *restaurant*?").
* **It cannot catch the dangerous misses**: a slang word spelled like a
  common one (*lit*, *sus*) or an idiom of common words. Those need the
  other two routes -- the person's correction saved to the same glossary,
  or meanings shown where they matter.
* **The cheaper detector is at least as good.** A word-count list of his
  own training text reads 33 of 40 at AUC 0.918 with no forward pass, so
  the build should read both and price them on real requests.

**What it does not settle.** Requests written by people other than the one
who wrote these 72; a threshold chosen on real traffic; whether the two
detectors combined beat either; any read of what he does with a glossary
line once it is on the page (findings 186-187 say a described word is not
yet read at 20M).
