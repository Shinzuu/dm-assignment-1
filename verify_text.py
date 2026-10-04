#!/usr/bin/env python3
"""Prove the reflow neither loses, duplicates nor reorders a single word.

reflow() rejoins hand-broken fragments and re-wraps them. That is a rewrite
of every line on every sheet, so the only safe check is a mechanical one:
the sequence of words going in must equal the sequence coming out, exactly.

Also flags lines a reader would trip over - orphans, stranded brackets,
doubled spaces, a sentence opening in lower case.

    python3 verify_text.py        # exits 1 on any problem
"""

import difflib
import re
import sys

import build
import content

WRAPPABLE = ("ln", "ind", "ind2", "quote")


def words_of(blocks):
    """Every word of every text block, in reading order."""
    out = []
    for b in blocks:
        if b[0] in WRAPPABLE:
            out.extend(b[1].split())
    return out


def check_stream():
    before = words_of(content.BLOCKS)
    after = words_of(build.reflow(content.BLOCKS))
    if before == after:
        print(f"  word stream identical ({len(before)} words)")
        return 0

    print(f"  WORD STREAM DIFFERS: {len(before)} in, {len(after)} out")
    sm = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
    shown = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        shown += 1
        if shown > 12:
            print("    ...")
            break
        ctx = " ".join(before[max(0, i1 - 6):i1])
        if tag == "delete":
            print(f'    LOST after "...{ctx}": {" ".join(before[i1:i2])!r}')
        elif tag == "insert":
            print(f'    ADDED after "...{ctx}": {" ".join(after[j1:j2])!r}')
        else:
            print(f'    CHANGED after "...{ctx}":')
            print(f'        was: {" ".join(before[i1:i2])!r}')
            print(f'        now: {" ".join(after[j1:j2])!r}')
    return 1


def check_readability():
    lines = [b for b in build.reflow(content.BLOCKS) if b[0] in WRAPPABLE]
    bad = []
    for i, b in enumerate(lines):
        t = b[1]
        if t.count("(") != t.count(")"):
            bad.append(("stranded bracket", t))
        if t.count("{") != t.count("}"):
            bad.append(("stranded brace", t))
        if t.count("[") != t.count("]"):
            bad.append(("stranded square bracket", t))
        if t.count('"') % 2:
            bad.append(("odd number of quote marks", t))
        if "  " in t:
            bad.append(("doubled space", t))
        if t != t.strip():
            bad.append(("stray whitespace", t))
        if re.search(r"\s[,.;:!?]", t):
            bad.append(("space before punctuation", t))
        if re.search(r"[a-z],[a-z]", t):
            bad.append(("comma with no space", t))
        if re.search(r"\.\s+[a-z]", t):
            bad.append(("lower case after a full stop", t))
        if len(t.split()) <= 2 and i and lines[i - 1][0] == b[0]:
            prev = lines[i - 1][1]
            if not prev.rstrip().endswith((".", ":", ";", "?", "!")):
                bad.append(("orphan line", f"{prev!r} / {t!r}"))
        if t.rstrip().endswith("-") and not t.rstrip().endswith("--"):
            bad.append(("line ends on a bare hyphen", t))
        if "\x00" in t:
            bad.append(("placeholder leaked", t))
        # a sentence can also open in lower case across a line break
        if i and lines[i - 1][0] == b[0]:
            prev = lines[i - 1][1].rstrip()
            if prev.endswith((".", "?", "!")) and re.match(r"[a-z]", t):
                bad.append(("lower case opens a sentence",
                            f"{prev[-28:]!r} / {t[:34]!r}"))
    if bad:
        for k, t in bad[:25]:
            print(f"    {k}: {t}")
        if len(bad) > 25:
            print(f"    ... {len(bad)} total")
    else:
        print(f"  no readability defects ({len(lines)} lines)")
    return len(bad)


def main():
    print("word stream")
    a = check_stream()
    print("readability")
    b = check_readability()
    total = a + b
    print(f"\n{total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
