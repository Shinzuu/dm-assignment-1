#!/usr/bin/env python3
"""Paginate content.py into F4 sheets and emit index.html.

The point of this script is that the handwriting constraint is enforced rather
than hoped for. Two hard checks:

  * no sheet carries more than LINES_PER_SHEET ruled lines;
  * no text line is wider than the writing area, so nothing silently wraps
    onto a second rule.

Either failure aborts the build.

    python3 build.py
"""

import html
import re
import sys
from datetime import date
from pathlib import Path

import content

HERE = Path(__file__).parent
LINES_PER_SHEET = 32

# Writing area is 176 mm wide at a 6.35 mm type size. IBM Plex Sans averages
# about 0.52 em per character, so ~3.3 mm a character, so ~53 characters fit.
# Stop well short of that: a hand needs slack and so does a wide glyph run.
HARD_CHARS = 52
WARN_CHARS = 46
INDENT_COST = {"ind": 2, "ind2": 4}


class BuildError(Exception):
    pass


def line_cost(block):
    """How many ruled lines this block occupies."""
    kind = block[0]
    if kind == "blank":
        return 1
    if kind in ("q", "h", "ln", "ind", "ind2", "math", "quote"):
        return 1
    if kind == "table":
        _, headers, rows, _ = block
        return 1 + len(rows)
    if kind == "draw":
        _, title, lines = block
        return 1 + len(lines)
    raise BuildError(f"unknown block kind: {kind!r}")


def atomic(block):
    """Blocks that must not be split across a sheet boundary."""
    return block[0] in ("table", "draw")


def check_widths(blocks):
    """Refuse to build if any line would overflow its rule."""
    problems, warnings = [], []
    for i, block in enumerate(blocks):
        kind = block[0]
        texts = []
        if kind in ("q", "h", "ln", "ind", "ind2", "math", "quote"):
            texts = [(block[1], INDENT_COST.get(kind, 0))]
        elif kind == "draw":
            texts = [(block[1], 0)] + [(ln, 1) for ln in block[2]]
        elif kind == "table":
            continue  # table cells are sized by the browser, not by us
        for text, indent in texts:
            width = len(text) + indent
            if width > HARD_CHARS:
                problems.append((i, width, text))
            elif width > WARN_CHARS:
                warnings.append((i, width, text))
    for i, w, t in warnings:
        print(f"  note: block {i} is {w} chars (soft limit {WARN_CHARS}): {t[:48]}")
    if problems:
        for i, w, t in problems:
            print(f"  OVERFLOW block {i}: {w} chars > {HARD_CHARS}: {t}", file=sys.stderr)
        raise BuildError(f"{len(problems)} line(s) too wide for the sheet")


def paginate(blocks, per_sheet=LINES_PER_SHEET):
    """One problem per group; balance each group over its sheets.

    Greedy filling at 32 leaves orphan tails - a sheet holding two leftover
    lines. Instead, work out how many sheets a problem needs, then spread it
    evenly over exactly that many, so the last sheet is never nearly empty.
    """
    groups, cur = [], []
    for block in blocks:
        if block[0] == "q" and cur:
            groups.append(cur)
            cur = []
        cur.append(block)
    if cur:
        groups.append(cur)

    sheets = []
    for group in groups:
        total = sum(line_cost(b) for b in group)
        needed = max(1, -(-total // per_sheet))          # ceil
        target = min(per_sheet, -(-total // needed))     # even split

        sheet, used = [], 0
        for block in group:
            cost = line_cost(block)
            if cost > per_sheet:
                raise BuildError(f"block {block[0]!r} needs {cost} lines, sheet holds {per_sheet}")
            # overflow the balanced target only up to the real limit, and only
            # when an atomic block would otherwise be stranded
            limit = target if not atomic(block) else per_sheet
            if sheet and used + cost > limit:
                while sheet and sheet[-1][0] == "blank":
                    sheet.pop()
                    used -= 1
                sheets.append(sheet)
                sheet, used = [], 0
            if not sheet and block[0] == "blank":
                continue
            sheet.append(block)
            used += cost
        if sheet:
            while sheet and sheet[-1][0] == "blank":
                sheet.pop()
            sheets.append(sheet)
    return sheets


def esc(s):
    return html.escape(s, quote=False)


def render_block(block):
    kind = block[0]
    if kind == "blank":
        return '<div class="blank"></div>'
    if kind == "q":
        return f'<p class="ln q">{esc(block[1])}</p>'
    if kind == "h":
        return f'<p class="ln h">{esc(block[1])}</p>'
    if kind == "ln":
        return f'<p class="ln">{esc(block[1])}</p>'
    if kind == "ind":
        return f'<p class="ln indent">{esc(block[1])}</p>'
    if kind == "ind2":
        return f'<p class="ln indent2">{esc(block[1])}</p>'
    if kind == "math":
        return f'<p class="ln math">{esc(block[1])}</p>'
    if kind == "quote":
        return f'<p class="ln quote">{esc(block[1])}</p>'
    if kind == "draw":
        _, title, lines = block
        body = "".join(f"<span>{esc(l)}</span>" for l in lines)
        inner = f"<b>{esc(title)}</b>" + "".join(
            f'<p class="ln">{esc(l)}</p>' for l in lines
        )
        return f'<div class="draw">{inner}</div>'
    if kind == "table":
        _, headers, rows, aligns = block
        th = "".join(
            f'<th class="{"n" if a == "r" else ""}">{esc(h)}</th>'
            for h, a in zip(headers, aligns)
        )
        trs = []
        for row in rows:
            tds = "".join(
                f'<td class="{"n" if a == "r" else ""}">{esc(str(c))}</td>'
                for c, a in zip(row, aligns)
            )
            trs.append(f"<tr>{tds}</tr>")
        return f"<table><tr>{th}</tr>{''.join(trs)}</table>"
    raise BuildError(f"cannot render {kind!r}")


def question_of(sheet, fallback):
    for block in sheet:
        if block[0] == "q":
            return block[1]
    return fallback


def main():
    blocks = content.BLOCKS
    print(f"blocks: {len(blocks)}")

    check_widths(blocks)
    sheets = paginate(blocks)

    for n, sheet in enumerate(sheets, 1):
        used = sum(line_cost(b) for b in sheet)
        if used > LINES_PER_SHEET:
            raise BuildError(f"sheet {n} holds {used} lines, limit {LINES_PER_SHEET}")
        print(f"  sheet {n:>2}: {used:>2}/{LINES_PER_SHEET} lines")

    total = sum(sum(line_cost(b) for b in s) for s in sheets)
    print(f"sheets: {len(sheets)}, ruled lines used: {total}")

    out, running = [], ""
    for n, sheet in enumerate(sheets, 1):
        running = question_of(sheet, running)
        body = "".join(render_block(b) for b in sheet)
        out.append(
            f'<section class="sheet" aria-label="Sheet {n} of {len(sheets)}">'
            f'<div class="body">{body}</div>'
            f'<span class="sheetq">{esc(running)}</span>'
            f'<span class="folio">{n} / {len(sheets)}</span>'
            f"</section>"
        )

    dates = "".join(
        f"<div><dt>{esc(label)}</dt><dd>{esc(value)}<em>{esc(note)}</em></dd></div>"
        for label, value, note in content.DATES
    )

    part = (
        '<div class="part">'
        "<h2>Part A &mdash; the eight solutions, to copy by hand</h2>"
        f"<p>{esc(content.SHEETS_INTRO)}</p>"
        f'<div class="howto">Submission is physical copies collected together '
        f"and handed to the Section Office, so these are written out, not printed.</div>"
        "</div>"
    )

    toolbar = (
        '<div class="zoombar"><div class="inner">'
        '<span class="lbl">Sheet size</span>'
        '<button id="zoomOut" type="button" aria-label="Smaller">A&minus;</button>'
        '<span class="pct" id="zoomPct" aria-live="polite">100%</span>'
        '<button id="zoomIn" type="button" aria-label="Bigger">A+</button>'
        '<button id="fitPage" type="button" data-mode="page">Fit whole sheet</button>'
        '<button id="fitWidth" type="button" data-mode="width">Fit width</button>'
        '<span class="spacer"></span>'
        f'<span class="hint">{len(sheets)} sheets &middot; keys + &minus; 0</span>'
        '</div></div>'
    )

    part += (
        toolbar
        + f'<div class="sheets"><div class="sheetwrap">{"".join(out)}</div></div>'
    )

    # ---------------- Part B ----------------
    pb, toc = [], []
    for block in content.PARTB:
        k = block[0]
        if k == "sec":
            _, sid, title = block
            toc.append((sid, title))
            pb.append(f'<h3 id="{sid}">{esc(title)}</h3>')
        elif k == "p":
            pb.append(f"<p>{esc(block[1])}</p>")
        elif k == "flag":
            pb.append(f'<p class="flag">{esc(block[1])}</p>')
        elif k == "warn":
            pb.append(f'<p class="warn">{esc(block[1])}</p>')
        elif k == "math":
            pb.append(f'<p class="fml">{esc(block[1])}</p>')
        elif k == "work":
            _, title, lines = block
            body = "\n".join(esc(l) for l in lines)
            pb.append(
                f'<figure class="work"><figcaption>{esc(title)}</figcaption>'
                f"<pre>{body}</pre></figure>"
            )
        elif k == "tbl":
            headers, rows = block[1], block[2]
            aligns = block[3] if len(block) > 3 else "l" * len(headers)
            th = "".join(f"<th>{esc(h)}</th>" for h in headers)
            trs = "".join(
                "<tr>" + "".join(f"<td>{esc(str(c))}</td>" for c in row) + "</tr>"
                for row in rows
            )
            pb.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
        else:
            raise BuildError(f"unknown Part B block {k!r}")

    tocnav = "".join(f'<a href="#{sid}">{esc(t)}</a>' for sid, t in toc)
    part += (
        '<div class="part partb">'
        "<h2>Part B &mdash; revision for the final</h2>"
        f"<p>{esc(content.PARTB_INTRO)}</p>"
        f'<nav class="toc">{tocnav}</nav>'
        "</div>"
        f'<div class="guide">{"".join(pb)}</div>'
    )

    tpl = (HERE / "template.html").read_text()
    page = (
        tpl.replace("__TITLE__", esc(content.TITLE))
        .replace("__COURSE__", esc(content.COURSE))
        .replace("__BLURB__", esc(content.BLURB))
        .replace("__META__", esc(content.BLURB))
        .replace("__DATES__", dates)
        .replace("__CONTENT__", part)
        .replace(
            "__BUILTLINE__",
            f"{len(sheets)} sheets at {LINES_PER_SHEET} ruled lines each. "
            f"Rebuilt {date.today().isoformat()} by build.py.",
        )
    )

    if "__" in re.sub(r"__[A-Z]+__", "", page):
        pass  # harmless; only guard against unreplaced tokens below
    leftover = re.findall(r"__[A-Z_]+__", page)
    if leftover:
        raise BuildError(f"unreplaced template tokens: {sorted(set(leftover))}")

    (HERE / "index.html").write_text(page)
    kb = len(page) / 1024
    print(f"wrote index.html ({kb:.1f} KB)")


if __name__ == "__main__":
    try:
        main()
    except BuildError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        sys.exit(1)
