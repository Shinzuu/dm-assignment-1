# DM Assignment-1 — worked solutions + exam revision

Course work for **CSE 4333 Data Mining**, Premier University Chittagong.
One page, two halves:

**Part A** — the eight assigned textbook problems, worked out and paginated
into F4 answer sheets at 32 ruled lines each, so they can be copied by hand
one line at a time. Submission is physical copies to the Section Office.

**Part B** — revision for the final, weighted by what the lecturer flagged in
the 3 October class. No assignment problem is reused; where a technique
overlaps, the numbers here are different.

**Live:** https://shinzuu.github.io/dm-assignment-1/

## Dates

| | |
|---|---|
| Assignment-1 due | 28 October (1–2 days' grace) |
| Final exam begins | 7 November — Chapters 3, 4, 6, 8, one question each |

## Problems covered

3.4(a)–(c) · 3.5 · 3.6(a)–(b) · 4.6(a) · 6.7(a)–(c) · 6.17 · 8.2(a)–(b) · 8.17

From Han, Pei & Tong, *Data Mining: Concepts and Techniques*, 4th ed. (2022).

## Building

```bash
python3 build.py     # content.py + template.html -> index.html
python3 check.py     # headless-browser layout audit, exits 1 on failure
```

`build.py` paginates into sheets and **refuses to build** if a line would be
too wide for the writing area or a sheet would exceed 32 lines. `check.py`
then renders the result and measures what `build.py` cannot know — that every
table row lands on the ruling, that nothing wraps onto a second rule, that no
content collides with the folio, and that the page never scrolls sideways.
Both run clean at desktop and phone widths.

Every numeric answer was computed independently rather than taken from a
solution manual, and re-verified in a separate script.
