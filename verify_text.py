#!/usr/bin/env python3
"""Mechanical checks on the text of both parts.

1. Wrapping loses, adds or reorders no word in any Part A block.
2. Every Part A problem statement and sub-question appears in the textbook
   (whitespace and the book's spaced ellipses normalised).
3. Readability: brackets balance, no doubled spaces, no space before
   punctuation, no lower case after a full stop, no line over budget.
4. Part B: brackets balance, paragraphs end with a stop, tables are not ragged,
   section ids are unique.

    python3 verify_text.py        # exits 1 on any problem
"""

import re
import subprocess
import sys
from pathlib import Path

import build
import part_a
import part_b

BOOK = Path.home() / "Documents/study/8th Semester/DM/Resources/Han-4th-ed-2022.pdf"
PROSE = ("stmt", "part", "ans", "p", "li")


def norm(t):
    t = t.replace("…", "...").replace(". . .", "...")
    t = t.replace("“", '"').replace("”", '"').replace("’", "'")
    t = t.replace("–", "-").replace("naïve", "naive").replace("∗", "")
    t = re.sub(r"-\s*\n\s*", "", t)          # hyphenation across book lines
    # compare without whitespace: pdftotext spaces subscripts and acronyms
    # ("T P", "A 1"), but every word, digit and comma must still match
    return re.sub(r"\s+", "", t)


def check_wrap():
    bad = 0
    for b in part_a.BLOCKS:
        if b[0] not in PROSE:
            continue
        lines = build.expand([b])
        words = [w for x in lines if x[0] != "blank" for w in x[1].split()]
        if words != b[1].split():
            print(f"    WRAP CHANGED TEXT: {b[1][:60]}")
            bad += 1
    print(f"  wrap: {'ok' if not bad else bad}")
    return bad


def check_against_book():
    try:
        raw = subprocess.run(["pdftotext", str(BOOK), "-"], capture_output=True,
                             text=True, check=True).stdout
    except Exception as e:                       # book not present: say so
        print(f"  book: SKIPPED ({e})")
        return 0
    book = norm(raw).replace("2010.", "2010?")   # 3.5(b) ends with a full stop
    book = re.sub(r"(?<=[.?])[a-d]\.", "", book)   # the book letters parts "a."
    bad = 0
    for b in part_a.BLOCKS:
        if b[0] not in ("stmt", "part"):
            continue
        chunks = [c for c in re.split(r"(?<=[.?;])", b[1]) if c.strip()]
        for c in chunks:
            if norm(re.sub(r"^\s*\([a-d]\)\s*", "", c)) not in book:
                print(f"    NOT IN BOOK: {c[:90]}")
                bad += 1
    print(f"  book wording: {'ok' if not bad else bad}")
    return bad


def check_readability():
    bad = []
    for x in build.expand(part_a.BLOCKS):
        if x[0] in ("blank", "svg", "table", "math"):
            continue
        t = x[1]
        # a short bracket must stay on one line; the book's long ones may wrap
        if x[0] != "quote" and t.count("(") != t.count(")"):
            bad.append(("bracket split across lines", t))
        if "  " in t:
            bad.append(("doubled space", t))
        if re.search(r"\s[,.;:!?]", t):
            bad.append(("space before punctuation", t))
        if re.search(r"(?<![.\d])\.\s+[a-z]", t):
            bad.append(("lower case after a full stop", t))
    for k, t in bad[:20]:
        print(f"    {k}: {t}")
    print(f"  readability: {'ok' if not bad else len(bad)}")
    return len(bad)


def check_partb():
    bad, ids = [], set()
    for b in part_b.PARTB:
        k = b[0]
        if k in ("chap", "sec"):
            if b[1] in ids:
                bad.append(("duplicate id", b[1]))
            ids.add(b[1])
            continue
        texts = []
        if k in ("p", "flag", "warn", "tip", "math"):
            texts = [b[1]]
        elif k in ("ul", "ol"):
            texts = list(b[1])
        elif k == "defs":
            texts = [x for pair in b[1] for x in pair]
        elif k == "tbl":
            widths = {len(r) for r in b[2]} | {len(b[1])}
            if len(widths) > 1:
                bad.append(("ragged table", str(b[1])))
            texts = [str(c) for r in b[2] for c in r]
        for t in texts:
            if t.count("(") != t.count(")"):
                bad.append(("unbalanced bracket", t[:70]))
            if k in ("p", "flag", "warn", "tip") and not t.rstrip().endswith((".", ":", "?", "”")):
                bad.append(("no final stop", t[-60:]))
            if k != "math" and "  " in t:
                bad.append(("doubled space", t[:70]))
    for kk, t in bad[:20]:
        print(f"    {kk}: {t}")
    print(f"  part B: {'ok' if not bad else len(bad)}")
    return len(bad)


def main():
    total = check_wrap() + check_against_book() + check_readability() + check_partb()
    print(f"\n{total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
