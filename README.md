# DM Assignment-1 — worked solutions + exam revision

Course work for **CSE 4333 Data Mining**, Premier University Chittagong.
Three pages: a welcome that routes you to either half, then:

**Part A** — the eight assigned textbook problems on 21 F4 answer sheets at
32 ruled lines each, to copy by hand one line at a time. Each problem opens
with the book's exact statement in blue, then each sub-question and its
answer. Table rows are coloured: green kept, red pruned, yellow the result.

**Part B** — revision for the final, chapter by chapter: the theory to write
in words, then the slide examples worked in full (Manhattan k-means, the
buys_computer tree and naive Bayes, Apriori on the pasta data), plus Hopkins,
silhouette and complete linkage.

**Live:** https://shinzuu.github.io/dm-assignment-1/

## Dates

| | |
|---|---|
| Final exam | Wed 7 October, 2:00–5:00 PM — Chapters 3, 4, 6, 8, one question each |
| Assignment-1 due | 28 October (1–2 days' grace) |

## Problems covered

3.4(a)–(c) · 3.5 · 3.6(a)–(b) · 4.6(a) · 6.7(a)–(c) · 6.17 · 8.2(a)–(b) · 8.17

From Han, Pei & Tong, *Data Mining: Concepts and Techniques*, 4th ed. (2022).

## Building

```bash
python3 build.py        # part_a.py + part_b.py -> index.html, part-a.html, part-b.html
python3 verify_text.py  # wrapping loses no word; statements match the book
python3 check.py        # headless-browser audit of all three, exits 1 on failure
```

`build.py` paginates into sheets and **refuses to build** if a line would be
too wide for the writing area or a sheet would exceed 32 lines. `check.py`
then renders the result and measures what `build.py` cannot know — that every
table row lands on the ruling, that nothing wraps onto a second rule, that no
content collides with the folio, and that the page never scrolls sideways.
Both run clean at desktop and phone widths.

Every numeric answer was computed independently rather than taken from a
solution manual, and re-verified in a separate script.
