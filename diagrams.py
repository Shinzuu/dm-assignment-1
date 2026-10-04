"""Real diagrams for the sheets, so they can be copied one to one.

Each function returns (lines, svg). `lines` is how many ruled lines the
drawing occupies, so build.py can budget it exactly like any other block.
The SVG viewBox is 100 wide by (lines * 6.35) tall, matching the sheet's
line pitch, and the drawing scales with the sheet.
"""

W = 100.0          # viewBox width; the sheet scales it to the writing area
LH = 6.35          # one ruled line inside the viewBox


def _wrap(content_h, body):
    """Fit the drawing to whole ruled lines, never clipping it.

    content_h is the drawing's real extent in viewBox units. The viewBox is
    sized to that, then rounded up to whole lines, so the sheet's budget and
    the drawing always agree.
    """
    import math
    lines = max(1, math.ceil(content_h / LH))
    h = lines * LH
    return (lines, (
        f'<svg class="dg" viewBox="0 0 {W:g} {h:g}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" preserveAspectRatio="xMidYMid meet">{body}</svg>'
    ))


def _box(x, y, w, h, label, fields=(), fill="#fff"):
    # a box must be tall enough for its own field list, or the last line is
    # clipped by its own border
    if fields:
        h = max(h, 6.2 + 3.3 * len(fields))
    out = [f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="0.8" '
           f'fill="{fill}" stroke="#15203A" stroke-width="0.45"/>']
    out.append(f'<text x="{x + w/2:g}" y="{y + 3.6:g}" text-anchor="middle" '
               f'font-size="3" font-weight="700">{label}</text>')
    if fields:
        out.append(f'<line x1="{x:g}" y1="{y + 4.8:g}" x2="{x + w:g}" y2="{y + 4.8:g}" '
                   f'stroke="#15203A" stroke-width="0.3"/>')
        for i, f in enumerate(fields):
            out.append(f'<text x="{x + 1.4:g}" y="{y + 8.1 + i * 3.3:g}" '
                       f'font-size="2.5">{f}</text>')
    return "".join(out)


def _line(x1, y1, x2, y2, dash=False):
    d = ' stroke-dasharray="1.2 1"' if dash else ""
    return (f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
            f'stroke="#15203A" stroke-width="0.4"{d}/>')


def _txt(x, y, s, size=2.6, anchor="start", weight="400", style=""):
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}"{st}>{s}</text>')


# ---------------------------------------------------------------- schemas

def star_doctor():
    """3.4(b) — star schema on time, doctor, patient."""
    b = [
        _box(36, 22, 28, 20, "fee", ["time_key", "doctor_id", "patient_id", "count", "charge"], "#F3F7FB"),
        _box(4, 2, 26, 16, "time", ["time_key", "day", "month", "year"]),
        _box(70, 2, 26, 16, "doctor", ["doctor_id", "name", "phone", "specialty"]),
        _box(36, 48, 28, 16, "patient", ["patient_id", "name", "address", "gender"]),
        _line(30, 14, 40, 24), _line(70, 14, 60, 24), _line(50, 42, 50, 48),
    ]
    return _wrap(64, "".join(b))


def snowflake_university():
    """3.5(a) — snowflake schema, dimensions normalised one step out."""
    b = [
        _box(34, 20, 32, 19, "university",
             ["student_id, course_id", "semester_id, instructor_id", "count, avg_grade"], "#F3F7FB"),
        _box(2, 4, 22, 13, "student", ["student_id", "name, major_id"]),
        _box(2, 42, 22, 11, "major", ["major_id", "major_name"]),
        _box(76, 4, 22, 13, "course", ["course_id", "name, dept_id"]),
        _box(76, 42, 22, 11, "department", ["dept_id", "dept_name"]),
        _box(34, 48, 22, 11, "semester", ["semester_id", "semester, year"]),
        _box(60, 62, 24, 11, "instructor", ["instructor_id", "name, dept_id"]),
        _line(24, 12, 34, 24), _line(13, 17, 13, 42),
        _line(76, 12, 66, 24), _line(87, 17, 87, 42),
        _line(45, 39, 45, 48),
        _line(66, 36, 72, 62), _line(84, 53, 78, 62),
    ]
    return _wrap(74, "".join(b))


def star_spectator():
    """3.6(a) — star schema on date, spectator, location, game."""
    b = [
        _box(36, 24, 28, 20, "sales",
             ["date_key, game_id", "spectator_id", "location_id", "count, charge"], "#F3F7FB"),
        _box(2, 2, 26, 16, "date", ["date_key", "day, month", "quarter, year"]),
        _box(72, 2, 26, 16, "spectator", ["spectator_id", "name, category", "phone"]),
        _box(2, 50, 26, 16, "location", ["location_id", "name, city", "province"]),
        _box(72, 50, 26, 16, "game", ["game_id", "name, type", "description"]),
        _line(28, 14, 38, 26), _line(72, 14, 62, 26),
        _line(28, 54, 38, 42), _line(72, 54, 62, 42),
    ]
    return _wrap(70, "".join(b))


# ---------------------------------------------------------------- FP-tree

def fp_tree():
    """4.6(a) — the FP-tree, with counts on every node."""
    def node(x, y, lab):
        return (f'<circle cx="{x:g}" cy="{y:g}" r="3.4" fill="#fff" stroke="#15203A" stroke-width="0.45"/>'
                f'<text x="{x:g}" y="{y + 1.1:g}" text-anchor="middle" font-size="2.6" font-weight="600">{lab}</text>')
    b = [
        _box(38, 1, 18, 6, "root"),
        node(47, 14, "K:5"),
        node(34, 26, "E:4"), node(72, 26, "M:1"),
        node(22, 38, "M:2"), node(46, 38, "O:2"), node(72, 38, "Y:1"),
        node(22, 50, "O:1"), node(46, 50, "Y:1"),
        node(22, 62, "Y:1"),
        _line(47, 7, 47, 10.6),
        _line(45, 17, 36, 22.8), _line(50, 17, 70, 22.8),
        _line(32, 29, 24, 34.8), _line(37, 29, 44, 34.8), _line(72, 29.4, 72, 34.6),
        _line(22, 41.4, 22, 46.6), _line(46, 41.4, 46, 46.6),
        _line(22, 53.4, 22, 58.6),
        _box(84, 8, 15, 24, "header",
             ["K:5", "E:4", "M:3", "O:3", "Y:3"], "#F7F9FC"),
    ]
    return _wrap(67, "".join(b))


# ---------------------------------------------------------------- 6.7 tree

def decision_tree():
    """6.7(b) — the induced tree, salary at the root."""
    def leaf(x, y, lab, n):
        return (f'<rect x="{x:g}" y="{y:g}" width="19" height="5.6" rx="2.8" '
                f'fill="#EAF2E7" stroke="#15203A" stroke-width="0.4"/>'
                f'{_txt(x + 9.5, y + 3.9, f"{lab} ({n})", 2.4, "middle", "600")}')
    b = [_box(26, 1, 22, 6.4, "salary?", (), "#F3F7FB")]

    # five pure branches down the left, label then box, no crossing lines
    for i, (lab, cls, n) in enumerate([("26\u201330K", "junior", 46), ("31\u201335K", "junior", 40),
                                       ("36\u201340K", "senior", 4), ("41\u201345K", "junior", 4),
                                       ("66\u201370K", "senior", 8)]):
        y = 12 + i * 7.6
        b += [_txt(0, y + 3.9, lab, 2.4), leaf(15, y, cls, n),
              _line(37, y + 2.8, 34, y + 2.8), _line(34, y + 2.8, 34, y + 2.8)]
    b.append(_line(37, 7.4, 37, 50))                       # the trunk
    for i in range(5):
        y = 12 + i * 7.6
        b.append(_line(37, y + 2.8, 34, y + 2.8))
    b.append(_line(34, 14.8, 34, 45.2))

    # the one impure branch, carried on down
    b += [_txt(22, 54, "46\u201350K", 2.4),
          _box(32, 50, 26, 6.4, "department?", (), "#F3F7FB")]
    for i, (lab, cls, n) in enumerate([("sales", "senior", 30), ("systems", "junior", 23),
                                       ("marketing", "senior", 10)]):
        y = 60 + i * 7.6
        b += [_txt(62, y + 3.9, lab, 2.3), leaf(78, y, cls, n),
              _line(60, y + 2.8, 62, y + 2.8)]
    b += [_line(58, 53.2, 60, 53.2), _line(60, 53.2, 60, 73.2)]
    return _wrap(78, "".join(b))


# ---------------------------------------------------------------- ROC

def roc_curve():
    """6.17 — the ROC staircase, with the random-guess diagonal."""
    X0, Y0, S = 16.0, 56.0, 40.0          # origin and axis length
    def px(fpr): return X0 + fpr * S
    def py(tpr): return Y0 - tpr * S
    pts = [(0, 0), (0, .2), (.2, .2), (.2, .6), (.4, .6), (.4, .8), (.8, .8), (1, .8), (1, 1)]
    path = " ".join(("M" if i == 0 else "L") + f"{px(a):g},{py(b):g}" for i, (a, b) in enumerate(pts))
    b = [
        _line(X0, Y0, X0 + S, Y0), _line(X0, Y0, X0, Y0 - S),
        _line(X0, Y0, X0 + S, Y0 - S, dash=True),
        f'<path d="{path}" fill="none" stroke="#A8453F" stroke-width="0.7"/>',
    ]
    for t in (0, .2, .4, .6, .8, 1):
        b += [_line(px(t), Y0, px(t), Y0 + 1), _txt(px(t), Y0 + 4, f"{t:g}", 2.3, "middle"),
              _line(X0 - 1, py(t), X0, py(t)), _txt(X0 - 2, py(t) + .8, f"{t:g}", 2.3, "end")]
    for a, c in pts[1:]:
        b.append(f'<circle cx="{px(a):g}" cy="{py(c):g}" r="0.75" fill="#A8453F"/>')
    b += [_txt(X0 + S / 2, Y0 + 8, "FPR", 2.8, "middle", "600"),
          f'<text x="{X0 - 7:g}" y="{Y0 - S/2:g}" text-anchor="middle" font-size="2.8" '
          f'font-weight="600" transform="rotate(-90 {X0 - 7:g} {Y0 - S/2:g})">TPR</text>',
          _txt(X0 + S + 2, Y0 - S + 4, "AUC", 2.5, "start", "600"),
          _txt(X0 + S + 2, Y0 - S + 7.5, "= 0.64", 2.5),
          _txt(X0 + S * .55, Y0 - S * .3, "random", 2.2, "start", style="italic")]
    return _wrap(66, "".join(b))


def kmeans_plot():
    """8.2 — the eight points with the final three clusters ringed."""
    X0, Y0, S = 14.0, 54.0, 4.2
    def px(x): return X0 + x * S
    def py(y): return Y0 - y * S
    pts = {"A1": (2, 10), "A2": (2, 5), "A3": (8, 4), "B1": (5, 8),
           "B2": (7, 5), "B3": (6, 4), "C1": (1, 2), "C2": (4, 9)}
    groups = [(["A1", "B1", "C2"], "#A8453F"), (["A3", "B2", "B3"], "#1F6F4A"), (["A2", "C1"], "#2B4F8E")]
    b = [_line(X0, Y0, X0 + 10.5 * S, Y0), _line(X0, Y0, X0, Y0 - 11 * S)]
    for t in range(0, 11, 2):
        b += [_txt(px(t), Y0 + 3.6, str(t), 2.2, "middle"),
              _txt(X0 - 1.6, py(t) + .8, str(t), 2.2, "end")]
    for members, col in groups:
        xs = [pts[m][0] for m in members]; ys = [pts[m][1] for m in members]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        r = max(((x - cx) ** 2 + (y - cy) ** 2) ** .5 for x, y in zip(xs, ys)) * S + 4
        b.append(f'<ellipse cx="{px(cx):g}" cy="{py(cy):g}" rx="{r:g}" ry="{r:g}" fill="none" '
                 f'stroke="{col}" stroke-width="0.4" stroke-dasharray="1.4 1"/>')
        b.append(f'<path d="M{px(cx) - 1.6:g},{py(cy):g} L{px(cx) + 1.6:g},{py(cy):g} '
                 f'M{px(cx):g},{py(cy) - 1.6:g} L{px(cx):g},{py(cy) + 1.6:g}" '
                 f'stroke="{col}" stroke-width="0.5"/>')
    for name, (x, y) in pts.items():
        b.append(f'<circle cx="{px(x):g}" cy="{py(y):g}" r="1.1" fill="#15203A"/>')
        b.append(_txt(px(x) + 2, py(y) - 1.2, name, 2.4))
    b += [_txt(X0 + 5.6 * S, Y0 + 7.4, "x", 2.6, "middle", "600", "italic"),
          f'<text x="{X0 - 6:g}" y="{Y0 - 5.5 * S:g}" text-anchor="middle" font-size="2.6" '
          f'font-weight="600" font-style="italic" transform="rotate(-90 {X0 - 6:g} {Y0 - 5.5 * S:g})">y</text>',
          _txt(X0 + 7.6 * S, Y0 - 10 * S, "+ = final centre", 2.3)]
    return _wrap(63, "".join(b))


REGISTRY = {
    "star_doctor": star_doctor,
    "snowflake_university": snowflake_university,
    "star_spectator": star_spectator,
    "fp_tree": fp_tree,
    "decision_tree": decision_tree,
    "roc_curve": roc_curve,
    "kmeans_plot": kmeans_plot,
}
