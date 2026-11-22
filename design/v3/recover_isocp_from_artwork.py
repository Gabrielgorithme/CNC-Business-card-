"""Rebuilds isocp_fusion_strokes.json (needed by lettering.py, not committed) from the committed artwork.

The preferred source is still Fusion itself (cam/dump_isocp_from_fusion.py). Use this when Fusion is not at hand:
v3_*_artwork.svg holds every text as one <path>, written by generate.T() in call order. Replaying those calls
gives each text's string, origin, height and spacing; the strokes then split into glyphs along x, and the
advances come out of a least-squares fit over all texts. Glyphs agree between texts to under 0.001 mm, which is
the rounding of the SVG. Only characters present in the artwork are recovered, and generate.py must be the
version that wrote the artwork.

    python design/v3/recover_isocp_from_artwork.py          # writes isocp_fusion_strokes.json next to this file
"""
import sys, re, json, types, pathlib, collections
import numpy as np
HERE = pathlib.Path(__file__).parent
CAP_RATIO, MIN_HEIGHT = 0.8775, 0.70        # as measured in Fusion: capital height / text-height setting; smallest height used
SUB = {"—": "-", "–": "-", "…": "...", "μ": "µ", "−": "-"}
SIDE = 1.4625                               # ISOCP side bearing at height 10: every cell is ink width + 2 x this
FRACTION = {"start": 0.0, "middle": 0.5, "end": 1.0}

def replay():
    """The T() calls of both faces, in order, without needing the stroke data."""
    stub = types.ModuleType("lettering"); stub.MIN_HEIGHT, stub.CAP_RATIO = MIN_HEIGHT, CAP_RATIO
    stub.layout = lambda *a, **k: ([], 0.0); stub.depth_for = lambda cap: 0.05
    sys.modules["lettering"] = stub; sys.path.insert(0, str(HERE))
    import generate as G
    calls = []
    def T(x, y, s, size, weight=500, anchor="start", fill=None, ls=1.2, font=None, extra=""):
        h = max(MIN_HEIGHT, 0.729 * size / 10 / CAP_RATIO)
        calls.append(dict(x=x, y=y, s="".join(SUB.get(c, c) for c in s), h=h, sp=ls * 0.035 * h / 0.7, f=FRACTION[anchor])); return ""
    G.T = T; G.shade = lambda *a, **k: ""
    out = {}
    for name, fn in (("front", G.front), ("back", G.back)):
        calls.clear(); fn(); out[name] = list(calls)
    return out

def text_paths(svg):
    out = []
    for m in re.finditer(r'<path d="([^"]*)"([^>]*)>', svg):
        if 'stroke-linejoin="round"' in m.group(2):          # only T() writes this attribute
            out.append([[tuple(float(v) for v in p.split(",")) for p in sub.replace("L", " ").split()] for sub in m.group(1).split("M")[1:]])
    return out

def glyph_groups(strokes, eps):
    """Strokes of one text -> one list per glyph. Glyphs never overlap in x; the strokes of one glyph always do."""
    spans = sorted((min(p[0] for p in st), max(p[0] for p in st), n) for n, st in enumerate(strokes)); comps = []
    for x0, x1, n in spans:
        if comps and x0 <= comps[-1][0] + eps: comps[-1][0] = max(comps[-1][0], x1); comps[-1][1].append(n)
        else: comps.append([x1, [n]])
    assert all(sorted(c[1]) == list(range(min(c[1]), max(c[1]) + 1)) for c in comps), "a glyph's strokes are not contiguous"
    return [[strokes[n] for n in sorted(c[1])] for c in comps]

def main():
    texts = []
    for name, calls in replay().items():
        paths = text_paths((HERE / f"v3_{name}_artwork.svg").read_text(encoding="utf-8"))
        assert len(paths) == len(calls), f"{name}: {len(paths)} text paths in the artwork for {len(calls)} T() calls - generate.py and the artwork are out of step"
        for c, st in zip(calls, paths):
            c["groups"] = glyph_groups(st, 0.02 * c["h"])
            assert len(c["groups"]) == sum(ch != " " for ch in c["s"]), "cannot split %r into glyphs" % c["s"]
            texts.append(c)
    chars = sorted(set("".join(t["s"] for t in texts))); ink = [c for c in chars if c != " "]
    ia = {c: n for n, c in enumerate(chars)}; io = {c: len(chars) + n for n, c in enumerate(ink)}
    # left edge of every glyph, in SVG units:  x + h * (sum of advances before it - f * sum of all advances + its own left edge) + spacing terms
    rows, rhs = [], []
    for t in texts:
        s, h, n = t["s"], t["h"], len(t["s"]); g = iter(t["groups"])
        for i, c in enumerate(s):
            if c == " ": continue
            r = np.zeros(len(chars) + len(ink))
            for j in range(i): r[ia[s[j]]] += h
            for j in range(n): r[ia[s[j]]] -= t["f"] * h
            r[io[c]] += h
            rows.append(r); rhs.append(min(p[0] for st in next(g) for p in st) - t["x"] - 10 * t["sp"] * i + t["f"] * 10 * (n - 1) * t["sp"])
    A, b = np.array(rows), np.array(rhs); sol = np.linalg.lstsq(A, b, rcond=None)[0]
    adv = {c: float(sol[ia[c]]) for c in chars}
    seen = collections.defaultdict(list)
    for t in texts:
        s, h, n = t["s"], t["h"], len(t["s"]); g = iter(t["groups"])
        x0 = t["x"] - t["f"] * 10 * (sum(adv[c] * h / 10 for c in s) + (n - 1) * t["sp"]); pen = 0.0
        for c in s:
            if c != " ": seen[c].append((h, [[((p[0] - x0 - 10 * pen) / h, (t["y"] - p[1]) / h) for p in st] for st in next(g)]))
            pen += adv[c] * h / 10 + t["sp"]
    glyphs = {" ": {"adv": round(adv[" "], 4), "strokes": []}}; worst = 0.0
    for c in ink:
        assert len({tuple(len(st) for st in g) for _, g in seen[c]}) == 1, "glyph %r differs between texts" % c
        wsum = sum(h * h for h, _ in seen[c]); first = seen[c][0][1]
        mean = [[[sum(h * h * g[a][k][q] for h, g in seen[c]) / wsum for q in (0, 1)] for k in range(len(first[a]))] for a in range(len(first))]
        worst = max(worst, max(abs(g[a][k][q] - mean[a][k][q]) * h for h, g in seen[c] for a in range(len(mean)) for k in range(len(mean[a])) for q in (0, 1)))
        xs = [p[0] for st in mean for p in st]
        # a character that only ends left-aligned texts never shows its advance: fall back on the cell rule
        a_c = adv[c] if abs(adv[c] - (max(xs) + SIDE)) < 0.5 else max(xs) + SIDE
        glyphs[c] = {"adv": round(a_c, 4), "strokes": [[[round(x, 4), round(y, 4)] for x, y in st] for st in mean]}
    data = {"height_setting_mm": 10.0, "cap_height_mm": 10 * CAP_RATIO, "baseline_y": 0.0, "H_xmin": 0.0, "H_width": 0.0, "H_advance": 0.0,
            "source": "recovered from v3_*_artwork.svg; strokes are relative to the pen position on the baseline", "glyphs": glyphs}
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "isocp_fusion_strokes.json"
    out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print("%d characters from %d texts, fit residual %.4f mm, glyph spread between texts %.4f mm -> %s" % (len(glyphs), len(texts), np.abs(A @ sol - b).max() / 10, worst / 10, out))
    print("characters:", "".join(chars))

if __name__ == "__main__":
    main()
