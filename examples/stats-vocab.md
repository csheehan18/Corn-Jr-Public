---
# A `synonyms:` block teaches the pack layer what you call your columns.
# It can sit at the top of any .md or .txt in your packs folder -- this
# file, a guide you already have, or a file that is nothing but this
# header. It applies to every table in the folder: the `column` words
# count toward whichever header carries them.
#
# The built-in tier already covers generic English ("how tall" finds a
# Height column, "how quick" finds Speed), so entries here are for the
# words that are yours: what "take a hit" means is a fact about how you
# talk, not about English.
synonyms:
  - ask: take a hit
    column: Defense
  - ask: hit hard
    column: Attack
  - ask: fruit
    column: Yield (kg)
---

Prose under the header is an ordinary pack doc, answered by paragraph the
way any .md in the folder is. A file can be only the header, only prose,
or both.
