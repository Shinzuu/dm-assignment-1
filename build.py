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
import part_a
import part_b
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
TEXT = ("q", "h", "ln", "ind", "ind2", "math", "quote", "sub", "ansfirst")


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
        w = len(b[1]) + INDENT_COST.get(b[0], 0) + (len(LABEL) if b[0] == "ansfirst" else 0)
        if b[0] == "quote":
            w = int(w * 1.06)
        if b[0] == "math":
            w = int(w * 1.18)          # monospace runs wider than Plex Sans
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




TARGET_WORDS = 9          # a hand fits eight or nine words on one ruled line
STMT_CHARS = 47           # the serif statement runs slightly wider
LABEL = "Answer: "


def wrap(text, budget, first_budget=None):
    """Greedy word wrap. Keeps a bracketed group together on one line."""
    first_budget = budget if first_budget is None else first_budget
    prot = re.sub(r"\(([^()]{0,24})\)",
                  lambda m: "(" + m.group(1).replace(" ", "\x00") + ")", text)
    lines, line = [], ""
    for w in prot.split():
        lim = first_budget if not lines else budget
        cand = w if not line else line + " " + w
        if line and (len(cand) > lim or len(cand.split()) > TARGET_WORDS):
            lines.append(line)
            line = w
        else:
            line = cand
    if line:
        lines.append(line)
    # never end a paragraph on a single short word
    if len(lines) >= 2 and len(lines[-1].split()) == 1 and len(lines[-2].split()) > 3:
        a = lines[-2].split()
        moved = a.pop() + " " + lines[-1]
        if len(moved) <= budget:
            lines[-2], lines[-1] = " ".join(a), moved
    return [l.replace("\x00", " ") for l in lines]


def expand_units(blocks):
    """Group ruled lines into units the paginator moves as one.

    Each unit: (lines, keep, breakable).
      keep       never end a sheet on this unit; it needs the start of the next
      breakable  a long paragraph may split, but leaves at least 2 lines on
                 each side; units of 3 lines or fewer move whole
    """
    units = []

    def add(lines, keep=False, breakable=True):
        units.append((lines, keep, breakable))

    def blank():
        if units and units[-1][0] != [("blank",)]:
            add([("blank",)], breakable=False)

    for b in blocks:
        k = b[0]
        if k == "q":
            blank()
            add([b], keep=True, breakable=False)
        elif k == "stmt":
            add([("quote", ln) for ln in wrap(b[1], STMT_CHARS)])
            blank()
        elif k == "part":
            blank()
            # a sub-question always stays on the sheet with its answer
            add([("quote", ln) for ln in wrap(b[1], STMT_CHARS)], keep=True,
                breakable=False)
        elif k == "ans":
            ls = wrap(b[1], HARD_CHARS - 2, HARD_CHARS - 2 - len(LABEL))
            lines = [("ansfirst", ls[0])] + [("ln", ln) for ln in ls[1:]]
            add(lines, keep=ls[-1].rstrip().endswith(":"))
        elif k == "p":
            ls = wrap(b[1], HARD_CHARS - 2)
            add([("ln", ln) for ln in ls], keep=ls[-1].rstrip().endswith(":"))
        elif k == "li":
            ls = wrap(b[1], HARD_CHARS - 2 - INDENT_COST["ind2"],
                      HARD_CHARS - 2 - INDENT_COST["ind"])
            add([("ind", ls[0])] + [("ind2", ln) for ln in ls[1:]])
        elif k in ("sub", "h"):
            add([b], keep=True, breakable=False)
        elif k == "blank":
            blank()
        else:
            add([b], breakable=False)
    return units


def expand(blocks):
    """One block per ruled line, in reading order."""
    return [ln for u in expand_units(blocks) for ln in u[0]]


def _cost(lines):
    return sum(line_cost(x) for x in lines)


def _start_need(u):
    """Lines of unit u that must fit for it to begin on this sheet."""
    lines, _, breakable = u
    c = _cost(lines)
    return min(c, 2) if breakable and len(lines) > 3 else c


def paginate(units, per_sheet=LINES_PER_SHEET):
    MIN_ROOM = 9    # a new problem only opens mid-sheet if this much room is left
    sheets, sheet = [], []

    def used():
        return _cost(sheet)

    def close():
        nonlocal sheet
        while sheet and sheet[-1][0] == "blank":
            sheet.pop()
        if sheet:
            sheets.append(sheet)
        sheet = []

    for i, u in enumerate(units):
        lines, keep, breakable = u
        if lines == [("blank",)] and not sheet:
            continue
        if lines[0][0] == "q" and sheet and per_sheet - used() < MIN_ROOM:
            close()
        # a chain of keep-units must fit together with the start of what follows
        need, j = 0, i
        while j < len(units) and units[j][1]:
            need += _cost(units[j][0])
            j += 1
        need += _start_need(units[j]) if j < len(units) else 0
        if i == j:
            need = _start_need(u)
        if sheet and used() + min(need, per_sheet) > per_sheet:
            close()
        if lines == [("blank",)] and not sheet:
            continue
        c = _cost(lines)
        if c > per_sheet:
            raise BuildError(f"{lines[0][0]!r} needs {c} lines, sheet holds {per_sheet}")
        if used() + c <= per_sheet:
            sheet.extend(lines)
            continue
        # a long paragraph splits: at least 2 lines here and 2 on the next sheet
        room = per_sheet - used()
        cut = min(room, len(lines) - 2)
        if breakable and len(lines) > 3 and cut >= 2:
            sheet.extend(lines[:cut])
            close()
            sheet.extend(lines[cut:])
        else:
            close()
            sheet.extend(lines)
    close()
    return sheets


def esc(s):
    return html.escape(str(s), quote=False)


def _p(cls, text):
    return f'<p class="{cls}">{esc(text)}</p>'


ROWCLS = {"ok": "rok", "no": "rno", "key": "rkey"}


def render(b):
    k = b[0]
    if k == "blank":
        return '<div class="blank"></div>'
    if k == "q":
        return _p("ln q", b[1])
    if k == "h":
        return _p("ln h", b[1])
    if k == "sub":
        return _p("ln sub", b[1])
    if k == "ln":
        return _p("ln", b[1])
    if k == "ansfirst":
        return f'<p class="ln"><b class="ans">Answer:</b> {esc(b[1])}</p>'
    if k == "ind":
        return _p("ln indent", b[1])
    if k == "ind2":
        return _p("ln indent2", b[1])
    if k == "math":
        return f'<p class="ln math">{esc(b[1])}</p>'
    if k == "quote":
        return _p("ln quote", b[1])
    if k == "svg":
        lines, svg = diagrams.REGISTRY[b[1]]()
        return f'<div style="height:calc({lines} * var(--pitch))">{svg}</div>'
    if k == "table":
        heads, rows, al = b[1], b[2], b[3]
        marks = b[4] if len(b) > 4 else {}
        th = "".join(f'<th class="{"n" if a == "r" else ""}">{esc(h)}</th>'
                     for h, a in zip(heads, al))
        trs = "".join(f'<tr class="{ROWCLS.get(marks.get(i), "")}">' + "".join(
            f'<td class="{"n" if a == "r" else ""}">{esc(c)}</td>'
            for c, a in zip(r, al)) + "</tr>" for i, r in enumerate(rows))
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
    blocks = expand(part_a.BLOCKS)
    check_widths(blocks)
    sheets = paginate(expand_units(part_a.BLOCKS))
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
        "<p>Start here. Theory, then the slide examples worked in full, chapter by chapter.</p>"
        "<ul><li>Ch 3: warehouse, cube, schemas, OLAP operations</li>"
        "<li>Ch 4: Apriori on the pasta data, rules, closed sets</li>"
        "<li>Ch 6: information gain, naive Bayes, metrics</li>"
        "<li>Ch 8: k-means (Manhattan), linkage, Hopkins, silhouette</li></ul></a>"
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

    # videos, on the home page, each opening in its own tab
    vids = ['<section class="videos"><h2>Watch first</h2>'
            f"<p>{esc(content.VIDEOS_INTRO)}</p>"]
    for group, items in content.VIDEOS:
        vids.append(f"<h3>{esc(group)}</h3><ul>")
        for vid, title, chan, why, first in items:
            tag = '<span class="first">start here</span>' if first else ""
            vids.append(
                f'<li><a href="https://www.youtube.com/watch?v={vid}" '
                f'target="_blank" rel="noopener noreferrer">{esc(title)}</a>'
                f'{tag}<span class="chan">{esc(chan)}</span>'
                f'<span class="why">{esc(why)}</span></li>')
        vids.append("</ul>")
    vids.append("</section>")
    body += "".join(vids)

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

    def inline(t):
        t = esc(t)
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)

    pb, toc, chapcol, open_card = [], [], "#2B5C8E", False
    for blk in part_b.PARTB:
        k = blk[0]
        if k == "chap":
            _, cid, label, title, col = blk
            chapcol = col
            if open_card:
                pb.append("</section>")
            toc.append((cid, label, title, col))
            pb.append(f'<section class="chap" id="{cid}" style="--c:{col}">'
                      f'<header><span>{esc(label)}</span><h2>{esc(title)}</h2></header>')
            open_card = True
        elif k == "sec":
            pb.append(f'<h3 id="{blk[1]}">{esc(blk[2])}</h3>')
        elif k == "p":
            pb.append(f"<p>{inline(blk[1])}</p>")
        elif k in ("ul", "ol"):
            pb.append(f"<{k}>" + "".join(f"<li>{inline(i)}</li>" for i in blk[1]) + f"</{k}>")
        elif k == "defs":
            pb.append('<dl class="defs">' + "".join(
                f"<div><dt>{inline(t)}</dt><dd>{inline(d)}</dd></div>" for t, d in blk[1])
                + "</dl>")
        elif k in ("flag", "warn", "tip"):
            lab = {"flag": "Named for the exam", "warn": "Trap", "tip": "In the exam"}[k]
            pb.append(f'<p class="{k}"><b>{lab}.</b> {inline(blk[1])}</p>')
        elif k == "math":
            pb.append(f'<p class="fml">{esc(blk[1])}</p>')
        elif k == "work":
            pb.append(f'<figure class="work"><figcaption>{esc(blk[1])}</figcaption>'
                      f'<pre>{chr(10).join(esc(l) for l in blk[2])}</pre></figure>')
        elif k == "tbl":
            heads, rows = blk[1], blk[2]
            marks = blk[3] if len(blk) > 3 else {}
            th = "".join(f"<th>{esc(h)}</th>" for h in heads)
            trs = "".join(f'<tr class="{ROWCLS.get(marks.get(i), "")}">'
                          + "".join(f"<td>{inline(str(c))}</td>" for c in r) + "</tr>"
                          for i, r in enumerate(rows))
            pb.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead>'
                      f"<tbody>{trs}</tbody></table></div>")
        else:
            raise BuildError(f"unknown Part B block {k!r}")
    if open_card:
        pb.append("</section>")
    tochtml = "".join(
        f'<a href="#{i}" style="--c:{c}"><span>{esc(l)}</span>{esc(t)}</a>'
        for i, l, t, c in toc)
    body = (
        '<div class="head"><h1>Part B &mdash; revision for the final</h1>'
        f'<p class="course">{esc(content.COURSE)}</p>'
        f"<p>{esc(part_b.INTRO)}</p>"
        f'<nav class="toc">{tochtml}</nav></div>'
        f'<div class="guide">{"".join(pb)}</div>')
    page("part-b.html", "Part B — DM revision for the final", body, nav("b"))


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print(f"build failed: {e}", file=sys.stderr)
        sys.exit(1)
