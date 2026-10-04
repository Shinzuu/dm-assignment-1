#!/usr/bin/env python3
"""Build three pages: a welcome, Part A (sheets), Part B (revision).

The handwriting constraint is enforced, not hoped for. The build aborts if a
line is wider than the writing area or a sheet exceeds its line budget.

    python3 build.py
"""

import html
import re
import sys
from datetime import date
from pathlib import Path

import content
import diagrams

HERE = Path(__file__).parent
LINES_PER_SHEET = 32

# Writing area is 176 mm at 6.35 mm type; IBM Plex Sans averages ~0.52 em a
# character, so ~53 fit. Stop short of that, and justify anything past
# JUSTIFY_CHARS so the writing reaches the right margin instead of trailing off.
HARD_CHARS = 52
WARN_CHARS = 48
JUSTIFY_CHARS = 43
INDENT_COST = {"ind": 2, "ind2": 4}
TEXT = ("q", "h", "ln", "ind", "ind2", "math", "quote")


class BuildError(Exception):
    pass


def line_cost(b):
    k = b[0]
    if k == "blank" or k in TEXT:
        return 1
    if k == "table":
        return 1 + len(b[2])
    if k == "svg":
        return diagrams.REGISTRY[b[1]]()[0]
    raise BuildError(f"unknown block {k!r}")


def atomic(b):
    return b[0] in ("table", "svg")


def check_widths(blocks):
    bad, warn = [], []
    for i, b in enumerate(blocks):
        if b[0] not in TEXT:
            continue
        w = len(b[1]) + INDENT_COST.get(b[0], 0)
        if w > HARD_CHARS:
            bad.append((i, w, b[1]))
        elif w > WARN_CHARS:
            warn.append((i, w, b[1]))
    for i, w, t in warn:
        print(f"  note: block {i} is {w} chars: {t[:46]}")
    if bad:
        for i, w, t in bad:
            print(f"  OVERFLOW block {i}: {w} > {HARD_CHARS}: {t}", file=sys.stderr)
        raise BuildError(f"{len(bad)} line(s) too wide")




def is_data(text):
    """True for a field list, a count list or similar: never merge as prose.

    Joining these welds one table's columns onto the next table's, or runs
    three separate itemset lines into one unreadable sentence.
    """
    if len([t for t in text.split() if "_" in t]) >= 2:
        return True                                   # snake_case field list
    if len(re.findall(r"\w+:\d", text)) >= 2:
        return True                                   # K:5, E:4, M:3 ...
    return False


TARGET_WORDS = 8          # what a hand comfortably fits on one ruled line


def reflow(blocks):
    """Join hand-broken lines back into sentences, then wrap to 8 words.

    The source keeps prose as short fragments, which left punctuation
    stranded mid-line and the right margin unused. Here consecutive fragments
    of the same kind are rejoined wherever the earlier one does not end a
    sentence, and the result is re-wrapped to TARGET_WORDS, bounded by the
    writing width.
    """
    WRAPPABLE = ("ln", "ind", "ind2", "quote")
    ENDS = (".", ":", ";", "?", "!")

    # A fragment that opens a list item, a labelled step or an all-caps
    # heading must stay on its own line; everything else is flowing prose and
    # can be rejoined into a paragraph.
    STARTS = re.compile(
        r"^(\d+\.\s|\d+:\s|\([a-z]\)\s|L\d\b|C\d\b|ROUND\b|Scan\b|\{|size \d|"
        r"[A-Z][A-Z][A-Z -]*$)")
    # a standalone heading or a label ending in a colon absorbs nothing
    STANDS_ALONE = re.compile(r"^[A-Z][A-Z0-9 /-]{2,}$")

    # 1. rejoin
    merged, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        if b[0] not in WRAPPABLE:
            merged.append(b)
            i += 1
            continue
        kind, text = b[0], b[1]
        j = i + 1
        # an ind2 line straight after an ind line is a hanging continuation of
        # the same sentence, so fold it in rather than leaving the indent to
        # jump mid-clause
        while j < len(blocks) and (blocks[j][0] == kind
                                   or (kind == "ind" and blocks[j][0] == "ind2")):
            nxt = blocks[j][1].lstrip()
            # a trailing comma says the list carries on, so let it join
            continues = text.rstrip().endswith(",")
            if ((STARTS.match(nxt) or is_data(text) or is_data(nxt))
                    and not continues
                    or STANDS_ALONE.match(text.strip())
                    or text.rstrip().endswith(":")):
                break
            # a trailing hyphen is a split word, not a word break
            joiner = "" if text.rstrip().endswith("-") else " "
            text = text.rstrip() + joiner + nxt
            j += 1
        merged.append((kind, text))
        i = j

    # 2. re-wrap
    out = []
    for b in merged:
        if b[0] not in WRAPPABLE:
            out.append(b)
            continue
        kind, text = b
        budget = HARD_CHARS - INDENT_COST.get(kind, 0)
        # keep a parenthesised group whole, so O(n log n) never breaks across
        # two lines and strands a bracket
        protected = re.sub(r"\(([^()]*)\)",
                           lambda m: "(" + m.group(1).replace(" ", "\x00") + ")", text)
        protected = re.sub(r"\[([^\[\]]*)\]",
                           lambda m: "[" + m.group(1).replace(" ", "\x00") + "]", protected)
        words, line, made = protected.split(), "", []
        for w in words:
            cand = w if not line else line + " " + w
            too_long = len(cand.replace("\x00", " ")) > budget
            too_many = len(cand.replace("\x00", " ").split()) > TARGET_WORDS
            if line and (too_long or too_many):
                made.append(line.replace("\x00", " "))
                line = w
            else:
                line = cand
        if line:
            made.append(line.replace("\x00", " "))
        # a paragraph ending on one or two words reads as a dropped fragment;
        # pull words back from the line above to even the last two out
        if len(made) >= 2 and len(made[-1].split()) <= 2:
            a, bl = made[-2].split(), made[-1].split()
            while len(bl) < 4 and len(a) > 3:
                bl.insert(0, a.pop())
                if len(" ".join(bl)) > budget:
                    a.append(bl.pop(0))
                    break
            made[-2], made[-1] = " ".join(a), " ".join(bl)

        # justify every line of the paragraph except its last
        for k, ln in enumerate(made):
            out.append((kind, ln, k < len(made) - 1))

    # never leave a one- or two-letter word stranded at the end of a line:
    # carry it down to join the word it belongs with
    SHORT = re.compile(r"\s+([A-Za-z]{1,2})$")
    for i in range(len(out) - 1):
        a, bnext = out[i], out[i + 1]
        if a[0] not in WRAPPABLE or bnext[0] != a[0]:
            continue
        m = SHORT.search(a[1])
        if not m:
            continue
        budget = HARD_CHARS - INDENT_COST.get(bnext[0], 0)
        moved = m.group(1) + " " + bnext[1]
        if len(moved) <= budget and len(moved.split()) <= TARGET_WORDS + 1:
            out[i] = (a[0], a[1][: m.start()]) + tuple(a[2:])
            out[i + 1] = (bnext[0], moved) + tuple(bnext[2:])
    return out


def paginate(blocks, per_sheet=LINES_PER_SHEET):
    """One problem per group, each group spread evenly over its sheets."""
    groups, cur = [], []
    for b in blocks:
        if b[0] == "q" and cur:
            groups.append(cur)
            cur = []
        cur.append(b)
    if cur:
        groups.append(cur)

    MIN_ROOM = 9    # a new problem only opens a sheet if the page is nearly full

    sheets, sheet, used = [], [], 0
    for g in groups:
        total = sum(line_cost(b) for b in g)
        room = per_sheet - used
        if sheet and room < MIN_ROOM:
            while sheet and sheet[-1][0] == "blank":
                sheet.pop()
            sheets.append(sheet)
            sheet, used = [], 0
            room = per_sheet
        # spread this problem over however many sheets it needs, counting the
        # part-filled sheet it is starting on
        for b in g:
            c = line_cost(b)
            if c > per_sheet:
                raise BuildError(f"{b[0]!r} needs {c} lines, sheet holds {per_sheet}")
            if sheet and used + c > per_sheet:
                while sheet and sheet[-1][0] == "blank":
                    sheet.pop()
                    used -= 1
                sheets.append(sheet)
                sheet, used = [], 0
            if not sheet and b[0] == "blank":
                continue
            sheet.append(b)
            used += c
    if sheet:
        while sheet and sheet[-1][0] == "blank":
            sheet.pop()
        sheets.append(sheet)
    return sheets


def esc(s):
    return html.escape(str(s), quote=False)


def _p(cls, text, indent=0, justify=None):
    """A ruled line. Justified unless it ends a paragraph."""
    if justify is None:
        justify = (len(text) + indent >= JUSTIFY_CHARS
                   and not text.rstrip().endswith(":"))
    if justify:
        cls += " j"
    return f'<p class="{cls}">{esc(text)}</p>'


def render(b):
    k = b[0]
    if k == "blank":
        return '<div class="blank"></div>'
    if k == "q":
        return _p("ln q", b[1], 0, b[2] if len(b) > 2 else None)
    if k == "h":
        return _p("ln h", b[1], 0, b[2] if len(b) > 2 else None)
    if k == "ln":
        return _p("ln", b[1], 0, b[2] if len(b) > 2 else None)
    if k == "ind":
        return _p("ln indent", b[1], 2, b[2] if len(b) > 2 else None)
    if k == "ind2":
        return _p("ln indent2", b[1], 4, b[2] if len(b) > 2 else None)
    if k == "math":
        return f'<p class="ln math">{esc(b[1])}</p>'
    if k == "quote":
        return _p("ln quote", b[1], 0, b[2] if len(b) > 2 else None)
    if k == "svg":
        lines, svg = diagrams.REGISTRY[b[1]]()
        return f'<div style="height:calc({lines} * var(--pitch))">{svg}</div>'
    if k == "table":
        _, heads, rows, al = b
        th = "".join(f'<th class="{"n" if a == "r" else ""}">{esc(h)}</th>'
                     for h, a in zip(heads, al))
        trs = "".join("<tr>" + "".join(
            f'<td class="{"n" if a == "r" else ""}">{esc(c)}</td>'
            for c, a in zip(r, al)) + "</tr>" for r in rows)
        return f"<table><tr>{th}</tr>{trs}</table>"
    raise BuildError(f"cannot render {k!r}")


PRINT_A = (
    "<style>@media print{@page{size:210mm 330mm;margin:0}}</style>"
)

ZOOM_JS = """
<script>
(function(){
  var sheets=document.querySelector('.sheets'); if(!sheets) return;
  var pct=document.getElementById('zoomPct');
  var EM=33.07, ASPECT=330/210, zoom=1, mode='page';
  function base(){var p=document.querySelector('.sheet');
    var z=parseFloat(getComputedStyle(sheets).getPropertyValue('--zoom'))||1;
    return parseFloat(getComputedStyle(p).fontSize)/z;}
  function clamp(z){return Math.min(4,Math.max(.35,z));}
  function apply(){sheets.style.setProperty('--zoom',zoom.toFixed(3));
    if(pct)pct.textContent=Math.round(zoom*100)+'%';
    document.querySelectorAll('.nav button[data-mode]').forEach(function(b){
      b.setAttribute('aria-pressed',String(b.dataset.mode===mode));});
    try{localStorage.setItem('dm1-zoom',JSON.stringify({z:zoom,m:mode}));}catch(e){}}
  function w(){return document.querySelector('.sheetwrap').clientWidth-32;}
  function fitWidth(){mode='width';zoom=clamp(w()/(EM*base()));apply();}
  function fitPage(){mode='page';var n=document.querySelector('.nav');
    var h=window.innerHeight-(n?n.offsetHeight:0)-30;
    zoom=clamp(Math.min(w()/(EM*base()),h/(EM*ASPECT*base())));apply();}
  function step(d){mode='manual';zoom=clamp(zoom*(d>0?1.12:1/1.12));apply();}
  document.getElementById('zoomIn').onclick=function(){step(1)};
  document.getElementById('zoomOut').onclick=function(){step(-1)};
  document.getElementById('fitPage').onclick=fitPage;
  document.getElementById('fitWidth').onclick=fitWidth;
  addEventListener('keydown',function(e){
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    var t=e.target.tagName; if(t==='INPUT'||t==='TEXTAREA')return;
    if(e.key==='+'||e.key==='='){step(1);e.preventDefault();}
    else if(e.key==='-'||e.key==='_'){step(-1);e.preventDefault();}
    else if(e.key==='0'){fitPage();e.preventDefault();}});
  var s=null; try{s=JSON.parse(localStorage.getItem('dm1-zoom')||'null');}catch(e){}
  if(s&&typeof s.z==='number'){zoom=clamp(s.z);mode=s.m||'manual';apply();}else{fitPage();}
  var t; addEventListener('resize',function(){ if(mode==='manual')return;
    clearTimeout(t); t=setTimeout(mode==='page'?fitPage:fitWidth,140);});
})();
</script>
"""


def nav(cur, extra=""):
    def tab(href, label, key):
        a = ' aria-current="page"' if key == cur else ""
        return f'<a class="tab" href="{href}"{a}>{label}</a>'
    return (
        '<nav class="nav"><div class="in">'
        '<a class="home" href="index.html">DM Assignment-1</a>'
        + tab("part-a.html", "Part A &middot; Assignment", "a")
        + tab("part-b.html", "Part B &middot; Revision", "b")
        + '<span class="sp"></span>' + extra
        + "</div></nav>"
    )


def page(path, title, body, navhtml, script="", sheets=0):
    tpl = (HERE / "template.html").read_text()
    out = (tpl.replace("__TITLE__", esc(title))
              .replace("__META__", esc(content.BLURB))
              .replace("__NAV__", navhtml)
              .replace("__BODY__", body)
              .replace("__SCRIPT__", script)
              .replace("__BUILTLINE__",
                       (f"{sheets} F4 sheets at {LINES_PER_SHEET} ruled lines. "
                        if sheets else "")
                       + f"Rebuilt {date.today().isoformat()}."))
    left = re.findall(r"__[A-Z_]+__", out)
    if left:
        raise BuildError(f"unreplaced tokens: {sorted(set(left))}")
    (HERE / path).write_text(out)
    print(f"  wrote {path} ({len(out)/1024:.1f} KB)")


def main():
    blocks = reflow(content.BLOCKS)
    check_widths(blocks)
    sheets = paginate(blocks)
    for n, sh in enumerate(sheets, 1):
        used = sum(line_cost(b) for b in sh)
        if used > LINES_PER_SHEET:
            raise BuildError(f"sheet {n} holds {used} lines")
    total = sum(sum(line_cost(b) for b in s) for s in sheets)
    print(f"sheets: {len(sheets)}  lines used: {total}")

    dates = "".join(f"<div><dt>{esc(l)}</dt><dd>{esc(v)}<em>{esc(n)}</em></dd></div>"
                    for l, v, n in content.DATES)

    body = (
        '<div class="head">'
        f"<h1>{esc(content.TITLE)}</h1>"
        f'<p class="course">{esc(content.COURSE)}</p>'
        f"<p>{esc(content.BLURB)}</p>"
        f'<dl class="dates">{dates}</dl></div>'
        '<div class="pick">'
        '<a href="part-b.html"><p class="when">Exam Wed 7 October</p>'
        "<h2>Part B &mdash; revision</h2>"
        "<p>Start here. Ordered by what he named aloud in the 3 October class.</p>"
        "<ul><li>What he said about the exam</li>"
        "<li>Hopkins, Silhouette, cluster count</li>"
        "<li>Worked maths on fresh numbers</li>"
        "<li>Traps that cost marks</li></ul></a>"
        '<a href="part-a.html"><p class="when">Due 28 October</p>'
        "<h2>Part A &mdash; the assignment</h2>"
        f"<p>All eight solutions on {len(sheets)} F4 sheets, sized to copy by hand "
        "one ruled line at a time.</p>"
        "<ul><li>3.4, 3.5, 3.6 &mdash; schemas and OLAP</li>"
        "<li>4.6 &mdash; Apriori and FP-growth</li>"
        "<li>6.7, 6.17 &mdash; trees, Bayes, ROC</li>"
        "<li>8.2, 8.17 &mdash; k-means and comparison</li></ul></a>"
        "</div>"
    )
    page("index.html", content.TITLE, body, nav("home"))

    out, running = [], ""
    for n, sh in enumerate(sheets, 1):
        for b in sh:
            if b[0] == "q":
                running = b[1]
        out.append(
            f'<section class="sheet" aria-label="Sheet {n} of {len(sheets)}">'
            f'<div class="body">{"".join(render(b) for b in sh)}</div>'
            f'<span class="sheetq">{esc(running)}</span>'
            f'<span class="folio">{n} / {len(sheets)}</span></section>')
    zoomctl = (
        '<button id="zoomOut" type="button" aria-label="Smaller">A&minus;</button>'
        '<span class="pct" id="zoomPct" aria-live="polite">100%</span>'
        '<button id="zoomIn" type="button" aria-label="Bigger">A+</button>'
        '<button id="fitPage" type="button" data-mode="page">Whole sheet</button>'
        '<button id="fitWidth" type="button" data-mode="width">Fit width</button>'
        f'<span class="meta">{len(sheets)} sheets &middot; + &minus; 0</span>')
    body = (
        '<div class="head"><h1>Part A &mdash; the eight solutions</h1>'
        f'<p class="course">{esc(content.COURSE)}</p>'
        f"<p>{esc(content.SHEETS_INTRO)}</p></div>"
        f'<div class="sheets"><div class="sheetwrap">{"".join(out)}</div></div>')
    page("part-a.html", "Part A — DM Assignment-1 solutions", body,
         nav("a", zoomctl), PRINT_A + ZOOM_JS, len(sheets))

    pb, toc = [], []
    for b in content.PARTB:
        k = b[0]
        if k == "sec":
            toc.append((b[1], b[2]))
            pb.append(f'<h3 id="{b[1]}">{esc(b[2])}</h3>')
        elif k == "p":
            pb.append(f"<p>{esc(b[1])}</p>")
        elif k in ("flag", "warn"):
            pb.append(f'<p class="{k}">{esc(b[1])}</p>')
        elif k == "math":
            pb.append(f'<p class="fml">{esc(b[1])}</p>')
        elif k == "work":
            pb.append(f'<figure class="work"><figcaption>{esc(b[1])}</figcaption>'
                      f'<pre>{chr(10).join(esc(l) for l in b[2])}</pre></figure>')
        elif k == "tbl":
            heads, rows = b[1], b[2]
            th = "".join(f"<th>{esc(h)}</th>" for h in heads)
            trs = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>"
                          for r in rows)
            pb.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead>'
                      f"<tbody>{trs}</tbody></table></div>")
        else:
            raise BuildError(f"unknown Part B block {k!r}")
    body = (
        '<div class="head"><h1>Part B &mdash; revision for the final</h1>'
        f'<p class="course">{esc(content.COURSE)}</p>'
        f"<p>{esc(content.PARTB_INTRO)}</p>"
        '<nav class="toc">'
        + "".join(f'<a href="#{i}">{esc(t)}</a>' for i, t in toc)
        + "</nav></div>"
        f'<div class="guide">{"".join(pb)}</div>')
    page("part-b.html", "Part B — DM revision for the final", body, nav("b"))


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print(f"build failed: {e}", file=sys.stderr)
        sys.exit(1)
