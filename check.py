#!/usr/bin/env python3
"""Audit the built page in a real browser and fail loudly on layout bugs.

build.py can only count lines. It cannot know that a table row rendered a
pixel taller than its budget, or that a cell wrapped onto a second rule. This
script loads index.html in headless Chrome and measures the result.

    python3 check.py            # desktop and phone
    python3 check.py 1280x1000  # one viewport

Exit code 1 if anything fails, so it can gate a deploy.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
CHROME = "google-chrome-stable"

PROBE = r"""
(() => {
  const out = {fail: [], warn: [], stat: {}};
  const d = document.documentElement;
  const sheets = [...document.querySelectorAll('.sheet')];
  out.stat.page = location.pathname.split('/').pop();

  const pitch = sheets.length
    ? parseFloat(getComputedStyle(sheets[0]).fontSize) * 1.4173 : 0;
  out.stat.sheets = sheets.length;
  out.stat.pitch = +pitch.toFixed(2);
  out.stat.viewport = [window.innerWidth, window.innerHeight];

  // the document itself must never scroll sideways
  if (d.scrollWidth > d.clientWidth + 1)
    out.fail.push(`document scrolls sideways: ${d.scrollWidth} > ${d.clientWidth}`);

  sheets.forEach((sh, i) => {
    const n = i + 1;
    const box = sh.getBoundingClientRect();
    const body = sh.querySelector('.body').getBoundingClientRect();
    const folio = sh.querySelector('.folio').getBoundingClientRect();

    // F4 aspect must hold
    const aspect = box.height / box.width;
    if (Math.abs(aspect - 330 / 210) > 0.01)
      out.fail.push(`sheet ${n}: aspect ${aspect.toFixed(3)} is not F4`);

    // content must not reach the folio or spill off the sheet
    if (body.bottom > folio.top)
      out.fail.push(`sheet ${n}: content overlaps the folio by ${(body.bottom - folio.top).toFixed(1)}px`);
    if (body.bottom > box.bottom)
      out.fail.push(`sheet ${n}: content runs off the bottom`);
    if (body.right > box.right + 1)
      out.fail.push(`sheet ${n}: content runs off the right edge`);

    // no line may silently wrap onto a second rule
    sh.querySelectorAll('.body p.ln').forEach(p => {
      const h = p.getBoundingClientRect().height;
      if (h > pitch * 1.55)
        out.fail.push(`sheet ${n}: a line wrapped (${h.toFixed(0)}px vs pitch ${pitch.toFixed(0)}px): "${p.textContent.slice(0, 40)}"`);
    });

    // tables must occupy exactly one pitch a row
    sh.querySelectorAll('table').forEach(t => {
      const rows = t.querySelectorAll('tr').length;
      const excess = t.getBoundingClientRect().height - rows * pitch;
      if (Math.abs(excess) > 2)
        out.fail.push(`sheet ${n}: table of ${rows} rows is ${excess.toFixed(1)}px off the ruling`);
      if (t.scrollWidth > t.clientWidth + 1)
        out.fail.push(`sheet ${n}: table overflows its column`);
    });

    // the dashed draw box must stay on the grid too
    sh.querySelectorAll('.draw').forEach(dw => {
      const kids = dw.querySelectorAll('b,p').length;
      const excess = dw.getBoundingClientRect().height - kids * pitch;
      if (Math.abs(excess) > 2)
        out.fail.push(`sheet ${n}: draw box is ${excess.toFixed(1)}px off the ruling`);
    });
  });

  // Part B
  out.stat.guideSections = document.querySelectorAll('.guide h3').length;
  out.stat.workedBoxes = document.querySelectorAll('.guide .work').length;


  // nothing anywhere may be wider than the viewport
  document.querySelectorAll('.masthead *, .part *, .guide > *, .zoombar *').forEach(el => {
    if (el.getBoundingClientRect().width > d.clientWidth + 1)
      out.fail.push(`element wider than viewport: ${el.tagName}.${el.className}`);
  });

  // anchors must resolve
  [...document.querySelectorAll('a[href^="#"]')].forEach(a => {
    const id = a.getAttribute('href').slice(1);
    if (id && !document.getElementById(id)) out.fail.push(`dead anchor #${id}`);
  });

  // zoom controls must exist and be wired
  if (sheets.length) {
    ['zoomIn','zoomOut','fitPage','fitWidth','zoomPct'].forEach(id => {
      if (!document.getElementById(id)) out.fail.push(`missing control #${id}`);
    });
  }
  // the nav must link both parts from every page
  ['part-a.html','part-b.html','index.html'].forEach(h => {
    if (!document.querySelector(`.nav a[href="${h}"]`)) out.fail.push(`nav missing link to ${h}`);
  });

  return out;
})()
"""


def probe(w, h, pagefile="part-a.html"):
    """Render index.html with the probe appended and read the JSON back.

    --dump-dom runs the page's JavaScript before dumping, so appending a
    script that writes its result into the DOM needs no debugging protocol
    and no third-party package.
    """
    page = (HERE / pagefile).read_text()
    injected = page.replace(
        "</body>",
        "<pre id=\"auditout\"></pre><script>setTimeout(function(){"
        "try{document.getElementById('auditout').textContent="
        "'@@'+JSON.stringify(" + PROBE.strip().rstrip(';') + ")+'@@';}"
        "catch(e){document.getElementById('auditout').textContent="
        "'@@'+JSON.stringify({fail:['probe threw: '+e.message],warn:[],stat:{}})+'@@';}"
        "},1200);</script></body>",
    )
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "audit.html"
        f.write_text(injected)
        for asset in ("template.html",):
            pass
        prof = Path(tmp) / "prof"
        out = subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
             f"--user-data-dir={prof}", "--hide-scrollbars",
             f"--window-size={w},{h}", "--virtual-time-budget=9000",
             "--dump-dom", f.as_uri()],
            capture_output=True, text=True, timeout=180,
        )
    dom = out.stdout
    if "@@" not in dom:
        raise RuntimeError("probe produced no output; chrome said: "
                           + (out.stderr or "")[-400:])
    raw = dom.split("@@")[1]
    return json.loads(html_unescape(raw))


def html_unescape(s):
    import html as _h
    return _h.unescape(s)


def main():
    sizes = [(1280, 1000), (390, 844)]
    pages = ["index.html", "part-a.html", "part-b.html"]
    if len(sys.argv) > 1:
        w, h = sys.argv[1].lower().split("x")
        sizes = [(int(w), int(h))]

    total = 0
    for w, h in sizes:
      for pg in pages:
        print(f"\n=== {pg}  {w} x {h}")
        r = probe(w, h, pg)
        st = r.get("stat", {})
        print(f"    sheets {st.get('sheets')}  pitch {st.get('pitch')}px  "
              f"Part B sections {st.get('guideSections')}  worked {st.get('workedBoxes')}")
        for m in r.get("warn", []):
            print(f"    warn: {m}")
        for m in r.get("fail", []):
            print(f"    FAIL: {m}")
        total += len(r.get("fail", []))
        if not r.get("fail"):
            print("    clean")

    print(f"\n{total} failure(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
