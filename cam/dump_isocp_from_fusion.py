"""Run inside Fusion (script or MCP): reads how Fusion draws Isocp.shx and writes the strokes to JSON.
design/v3/lettering.py needs that file (isocp_fusion_strokes.json, next to it). It is not committed because
the glyph data comes from Autodesk's font."""
import adsk.core, adsk.fusion, json, os

OUT = os.path.join(os.path.expanduser('~'), 'isocp_fusion_strokes.json')
CHARS = [chr(i) for i in range(32, 127)] + list('Ø±×·≈µÉé°²∅⌀')

def strokes(rc, txt):
    sk = rc.sketches.add(rc.xYConstructionPlane)
    ti = sk.sketchTexts.createInput2(txt, 1.0)            # height setting 10 mm
    ti.setAsMultiLine(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(60, 5, 0),
                      adsk.core.HorizontalAlignments.LeftHorizontalAlignment, adsk.core.VerticalAlignments.BottomVerticalAlignment, 0)
    ti.fontName = 'Isocp.shx'
    out = []
    for c in sk.sketchTexts.add(ti).explode():
        ev = c.geometry.evaluator
        _, t0, t1 = ev.getParameterExtents()
        _, pts = ev.getStrokes(t0, t1, 0.002)
        out.append([[round(p.x * 10, 4), round(p.y * 10, 4)] for p in pts])
    sk.deleteMe()
    return out

def xr(st):
    xs = [p[0] for s in st for p in s]
    return min(xs), max(xs)

def run(_context: str):
    rc = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    H = strokes(rc, 'H'); HH = strokes(rc, 'HH')
    x0, x1 = xr(H); ys = [p[1] for s in H for p in s]
    data = {'height_setting_mm': 10.0, 'cap_height_mm': max(ys) - min(ys), 'baseline_y': min(ys), 'H_xmin': x0,
            'H_width': x1 - x0, 'H_advance': xr(HH)[1] - x1, 'glyphs': {}}
    for ch in CHARS:
        a = strokes(rc, 'H' + ch); b = strokes(rc, 'H' + ch + 'H')
        data['glyphs'][ch] = {'adv': round(xr(b)[1] - xr(HH)[1], 4), 'strokes': a[len(H):]}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print('written', OUT)
