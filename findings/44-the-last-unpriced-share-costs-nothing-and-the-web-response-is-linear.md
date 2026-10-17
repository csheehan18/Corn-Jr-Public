# Forty-fourth finding — the last unpriced share costs nothing, and the web response is linear over two doses

`configs/mix_v1_temp5.py` ×2 against `mix_v1` ×4. One pair of slices moves: temporal
12,821,624 → 6,546,719 tokens (**9.79% → §4's declared 5.00%**), web taking all 4.79 points
(40.00% → 44.79%). Every other source is `mix_v1` verbatim, total held at 130,934,381, no
`repeat` anywhere.

**This is the sixth of §4's six shares.** It was written, pre-registered and committed on
2026-08-18 and then not run; it trained on 2026-08-19.

## Every behaviour row overlaps

`scripts/effect.py`, four baseline seeds against two arm seeds:

| row | `mix_v1` ×4 | `temp5` ×2 | verdict |
|---|---|---|---|
| `temporal.route` | 398-400 | **398, 398** | OVERLAP |
| `temporal.copy` | 353 | **353, 353** | OVERLAP |
| `tool.selection` | 112-156 | 146, 155 | OVERLAP |
| `tool.validity` | 157-175 | 171, 170 | OVERLAP |
| `tool.copy` | 100-120 | 119, 111 | OVERLAP |
| `tool.copy_wide` | 238-279 | 276, 276 | OVERLAP |
| `schema.conform` | 189-193 | 195, 194 | separated by 1, **churn unmeasured** |

`temporal.route` is the row that could have failed and the arm's real question: it reads
399/400 on `mix_v1` against a floor of 3, so it had one item of headroom up and 396 down.
**It did not move.** `temporal.copy` holds at 353/353, which is what §11's
cardinality-over-exposure rule predicted from a count taken before the run — 1,531 of 1,555
distinct date values survive the cut while exposure halves from 117.3 uses each to 60.8.

The one non-overlap is `schema.conform` by **one item**, on a row whose measured floor is 8.
`effect.py` reads it `churn unmeasured` and that is the right reading: it is not a result.

## Phase 1's research question is closed

| share | status |
|---|---|
| tools | priced — 25× too big, eleventh finding |
| structured | priced — 4× too big, fifteenth |
| conversational | filled and priced — twenty-fourth, twenty-fifth, twenty-seventh |
| narrative | priced — 19.58% → 10% costs no behaviour row |
| web | 40% → 44.79% here, and the receiver throughout |
| **temporal** | **priced here — 9.79% → 5.00% costs no behaviour row** |

**Six of six.** `mix_v2` is now a build rather than a research question. And the result is the
same shape the other five had: §4's declared share was right and the inherited one was
generous. Every share this project has priced has been too big, and none has ever been too
small.

## The web response is linear, and this is the first reading of that

Both `mix_v1_narr10` and this arm give their freed budget to web, at different sizes, so
together they are two doses on one receiver — which the config pre-registered as "the first
linearity reading this project can take".

| corpus | web share | `lm web` |
|---|---|---|
| `mix_v1` ×4 | 40.00% | 0.9020, 0.9023, 0.9024, 0.9034 |
| **`temp5` ×2** | **44.79%** | **0.8920, 0.8930** |
| `narr10` ×2 | 49.58% | 0.8844, 0.8844 |

Full dose: −0.01809 over 9.58 points, **−0.001888 per point**. Half dose: −0.01001 over 4.79
points, **−0.002090 per point**.

**The linear prediction for this arm was 0.8935 and it read 0.8925 — an error of −0.00097
against a floor of 0.0038.** The response is linear to a quarter of the resolution this design
can measure, slightly superlinear at the smaller dose in a direction the noise cannot separate.

That is worth having because it is what licenses the arithmetic `mix_v2` needs: web's share can
be set by interpolation rather than by another arm.

`lm temporal` reads 0.0966 and 0.0981 against a baseline of 0.0939-0.0973 — the pre-registered
degradation, in the right direction and **not separated**, one seed inside and one just
outside. The config permitted a degradation here on the grounds that the row reads ablations
even though it is saturated as a capacity instrument; what it got is a move too small to claim.

## The prediction was quoted as a result before it was one

`mix_v1_daylog`'s docstring pre-registers its own `temporal.copy` on the grounds that
"`mix_v1_temp5` halved this slice's read and **held 353/353** with 1,531 of 1,555 values
surviving". `mix_v1_conv10` opens with "`mix_v1_narr10` and `mix_v1_temp5` closed both". At the
time both were written, `mix_v1_temp5` had never trained: the count was real and in its
docstring, and the hold was a pre-registration.

**The prediction turned out right, which is the least useful way for this to end** — it means
the error cost nothing this time and the habit is intact. It is the same shape as the
forty-first finding's "56/120 wrong" and the seven share-claims the thirtieth finding
withdrew: a number stated once without its status attached, then read as settled by everything
downstream. The two docstrings are corrected to cite this finding.

## What this does not settle

- **Whether 5% is right**, only that 9.79% was not buying anything over it. The same limit
  `mix_v1_narr10` states about narrative. The marginal-rate framing that would settle it needs
  a third dose, and the cheap one is 2.5%.
- **The `tool.copy` question is still open and this arm cannot close it.** Pre-registered as
  such: the seventeenth finding's signal was 9 items and the thirtieth's floor on that row is
  28 frozen. 119 and 111 against 100-120 is exactly the unreadable overlap predicted.
- **Linearity is two points on one row.** Two doses define a line; they cannot show it is one.
  The reading is that 4.79 and 9.58 points are consistent with linear, not that the response is
  linear everywhere — and both doses are small, on one receiver, at 29.6M.
- **`schema.conform` +1 with churn unmeasured** is the only cell not plainly null, and the
  honest form is that nobody has measured churn on it rather than that it moved.
