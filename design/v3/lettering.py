"""Single-line lettering with ISOCP as Fusion draws it (Isocp.shx).

The stroke data was read out of Fusion itself (sketch text, height setting 10 mm, exploded),
so the geometry here is exactly what Fusion's own text tool produces.
`height` below is Fusion's text-height setting; the capital height is 0.8775 x height."""
import json, pathlib
_D = json.loads((pathlib.Path(__file__).parent / "isocp_fusion_strokes.json").read_text(encoding="utf-8"))
CAP_RATIO = _D["cap_height_mm"] / _D["height_setting_mm"]          # 0.8775
_LSB = (_D["H_advance"] - _D["H_width"]) / 2
_X0 = _D["H_xmin"] + _D["H_advance"] - _LSB                        # pen position after the reference 'H'
_SUB = {"—": "-", "–": "-", "…": "...", "μ": "µ", "−": "-"}
MIN_HEIGHT = 0.70                                                  # smallest Fusion text height [mm]
DEPTH_CLASSES = (0.05, 0.075, 0.10, 0.20)                          # V depth [mm]; line width = 2 x depth

def depth_for(cap_mm):
    """Line width aims at cap height / 9 (ISO lettering is h/10; this is the 'bold' side of it)."""
    want = cap_mm / 18
    return min(DEPTH_CLASSES, key=lambda d: abs(d - want) if d >= 0.05 else 9)

def layout(text, height_mm, spacing_mm=0.0):
    """Returns (polylines, width): strokes in mm, x to the right, y up, origin on the baseline."""
    k = height_mm / _D["height_setting_mm"]; x = 0.0; out = []
    for ch in text:
        ch = _SUB.get(ch, ch)
        for c in ch:
            g = _D["glyphs"].get(c)
            if g is None: raise KeyError("no ISOCP glyph for %r in %r" % (c, text))
            for s in g["strokes"]:
                out.append([(x + (px - _X0) * k, (py - _D["baseline_y"]) * k) for px, py in s])
            x += g["adv"] * k + spacing_mm
    return out, x - spacing_mm
