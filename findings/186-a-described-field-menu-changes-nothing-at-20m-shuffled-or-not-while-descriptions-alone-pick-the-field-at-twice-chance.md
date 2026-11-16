# He knows roughly what descriptions mean but ignores a described menu

**Full result:** At 20M, a one-line description beside each field moves the phrase -> field read by -0.04 to +0.03 on four checkpoints, the same menu with its descriptions rotated onto the wrong names reads within 0.03 of it on all four, and greedy decodes with and without the rotation open with the same words on nine of ten -- he does not read the menu -- while the descriptions alone, with no names, pick the right field 0.43-0.49 against a chance of 0.24; prediction held on the menu, missed high on descriptions alone

**Cost:** writing `scripts/probe_described.py` and its 66 descriptions 18:34-18:36 on 2026-10-20 (2d9e61f); the four reads 74.3 s and ten hand decodes 5.3 s on the card, both contended (the card at 38-40%, a bound).

**The owner's question, 2026-10-20.** The meaning hop is the wall findings
148, 156, 167-168, 183 and 184 each stopped at, and GENERATORS.md D5 says
there are two ways round it: put the hop in the bytes, or give it to the
runtime. Finding 34 has him picking a tool he never saw from its description.
Can he do the same for a *field* -- read "battery (how many hours it keeps
going between plugging in)" off the page and match "lasts all day unplugged"
to it? If he can, the runtime can supply meaning the weights lack; if he
cannot, that is the skill a generator built on our principles would have to
teach. Asked at 20M "to keep this small and a proof of the concept".

**The probe** (registered at 2d9e61f before any read). The understanding
ruler's 141 phrase -> field items over 30 kinds, scored exactly as the ruler
scores (what the phrase adds, three frames), four ways: `names` (the ruler);
`described` (a menu above the frame -- "Ways to compare a laptop: price (the
money you pay to buy it), weight (how heavy it is), ..."); `shuffled` (the
same menu with the descriptions rotated one place, so each name carries
another field's description -- the twin); `desc-only` (no names; the
descriptions are the candidates). No description shares a content stem with
any phrase of its kind (`check_desc`), so a copied word cannot vote.

## The read

    run                    names   described   shuffled   desc-only   (chance 0.24)
    nano20m_v3             0.54    0.55        0.58       0.49
    nano20m_v3_seed2       0.50    0.53        0.50       0.43
    nano20m_v3_compiled    0.54    0.55        0.54       0.49
    nano20m_v3_plainweb    0.58    0.54        0.52       0.49

`names` reproduces the ruler on all four. **The menu does nothing a reader of
it would do.** If he read the descriptions, `shuffled` would fall below
`names`, because the rotated description points at a wrong name; it sits at
or above `names` on three of four. On the plain-web checkpoint both menus read
*below* `names` (0.54 and 0.52 against 0.58): there the extra text costs a
little and the rotation costs nothing further. The prediction (`described`
within +0.05 of `names`, `shuffled` within 0.03 of `described`) held on all
four.

**The hand read agrees and says more.** Greedy decodes of ten items after
"..., so what matters most is the" on `nano20m_v3_compiled`: with or without
the rotation the continuation opens with the same words on nine of ten and
is word-for-word the same on six ("the same? | The laptop is a laptop"), and none of the 30 decodes writes a field
name -- the bare frame reads as a question ("the best?", "the difference?").
The menu moves only the register, toward comparing ("the difference between
the two? | The first headphones are"). So the scored read is the only place a
field choice exists at 20M at all, and there the menu's content is unread.

**Descriptions alone carry most of what names carry.** `desc-only` reads 0.43-0.49,
twice chance and 0.05-0.09 under `names`, above the registered band of
0.30-0.45 on three of four. So the meaning is partly in him: "lasts all day
unplugged" sits nearer "how many hours it keeps going between plugging in"
than nearer "how many files it holds" with no word in common. What is missing
is the *link on the page* -- "this name goes with this description" -- which
is a binding he would have to read and carry to the answer, the shape of
skill findings 13 and 34 installed by training.

## What it licenses

* **At 20M, a described menu cannot carry meaning to him today**: the
  runtime supplying descriptions buys nothing without training, so the
  "give it to the runtime" half of D5 is not free here.
* **The proof-of-concept is a training question with a clean gate.** A
  slice where the only route to the right name is through its description --
  invented names (D3), the same description under different names across
  lines (D2), real or hand-written phrasings under ten sightings (D8, D9) --
  read on this probe with the names replaced by invented ones, where
  `names` is chance by construction and any rise is reading.
* **Not a capacity floor**: twice-chance matching with no shared words says
  the meaning the link would need is already partly there.

**What it does not settle.** Any size above 20M (finding 34's tool reading
was trained, at larger sizes); the wish read (description -> wish), not
probed; whether a menu written in the corpus's own format, rather than
prose, reads differently; one prompt wording for the menu.
