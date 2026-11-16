# A small dose matching how the owner talks moves him furthest

**Full result:** Short-reply OpenAssistant exchanges -- people asking an assistant things, best-ranked answers of 60 words or fewer, 252,008 tokens read twice in place of the same 504,016 tokens of SODA (Apache 2.0) -- make the owner's own typed messages less surprising to the 5M at both seeds: 4.937 and 4.958 nats a token against the control's 5.218 and 5.105, under the pre-registered 4.992. Narrative and web hold (0.4890 / 0.4898, 0.9539 / 0.9563, over the web line at seed 2 only). The pre-registered row is (r), against a predicted (n): a seventh of finding 211's EmpatheticDialogues dose moves his register as far (4.880 / 4.963 there). It does not move the 148 stand-in messages (3.833 / 3.862 against 3.987 / 3.828), which EmpatheticDialogues did: each source moves the register it carries, and the owner writes questions and requests. Replies stay level or below at 5M (68 and 47 of 148 by a blind hand read against 70 and 55; 47 is the lowest of any 5M arm read, inside the control's spread)

**Cost:** OASST2 download (54 MB), `scripts/prepare_oasst.py` (a first cut without the rank filter paired prompts with off-topic replies, caught by hand), the mix and the pre-registration 16:30-16:40 on 2026-10-22 (24c35aa); the chain 16:40-16:52, 12.2 min (contended, a bound); the blind hand read of 592 replies ~10 min. ETA 15 min of card, actual 12.2.

**The question** (owner, 2026-10-22: Apache 2.0 stays, so EmpatheticDialogues
is out; "Do the short reply"; option (A), the set at its own size). Finding
212: OpenAssistant's prompts are the closest text to the owner's own messages
of any source read (bigram 426); its long answers teach reciting.

## The read

    read                                           base s1   base s2   OASST s1  OASST s2  (ED, 211: s1 / s2)
    register: the owner's 69 messages (counts only) 5.218     5.105     4.937     4.958     4.880 / 4.963
      the 148 stand-ins                            3.987     3.828     3.833     3.862     3.766 / 3.814
    dose (tokens, in place of SODA)                --        --        504,016             3,426,510
    lm narrative                                   0.4864    0.4883    0.4890    0.4898
    lm web                                         0.9512    0.9522    0.9539    0.9563
    lm conversational (SODA held-out)              0.5579    0.5599    0.5605    0.5650    0.5671 / 0.5717
    coherence, blind hand read (of 148)            70        55        68        47        64 / 66
    swap, within: right / margin                   0.91/8.27 0.91/8.08 0.90/8.22 0.92/8.00
    knowing, matcher: admits unk / answerable      7 / 11    13 / 17   11 / 13   6 / 19

(`evals/results/oasst__register.txt`, `reply_oasst__*`; the owner's messages
read by the script and never printed.)

**The gates, as registered.** Fluency: holds. Register: yes, 4.937 and
4.958 under 4.992. **(r).**

## Read by hand

The replies are the control's kind; the OASST arm's openings lean to
questions back ("What do you mean?", the commonest three-word opening at
seed 1 "what do you" x12), and its failures are the familiar ones. Seed 2's
47 comes from more stock "That's great!" to bad news (a scratched car, a
burned dinner) and the self-doubt line; read beside the base pair's own 15
of spread, it is a direction to watch at the next size, not a cost by any
registered rule. The knowing matcher splits by seed, unchecked by hand.

## What it licenses

* **The match of register matters more than the volume**: a small set of
  people asking an assistant moved his expectation of the owner's messages
  as far as seven times as much everyday-news dialogue, and moved only that
  register. The 1.0 conversational plan should carry text in the register
  the owner actually writes in -- questions and requests -- under a
  licence the Apache weights can carry.
* **Short-reply OpenAssistant is that text, at 0.25M tokens**: it goes in
  the 1.0 conversational plan as a share (Apache 2.0, attribution in the
  model card). More of its kind is the next search, not a heavier repeat.
* **Replies are still a size question** (findings 208-209): read the reply
  reads again at 20M with this share in, and watch seed 2's direction there.

**What it does not settle.** Any size above 5M; whether a larger share of
the same kind moves the register further; the owner's register beyond 69
messages.
