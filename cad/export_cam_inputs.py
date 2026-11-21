"""Exports what the Fusion CAM needs, all in MODEL coordinates (mm):
card_v3_body.step, engraving traces and fills per face, and helper curves for the 2D operations."""
import math, pathlib, ezdxf, cadquery as cq
from shapely.geometry import box, Point, LineString, MultiLineString
from shapely.ops import linemerge, unary_union
import build_card as B
out = pathlib.Path(__file__).parent
KEEP = Point(*B.SPR).buffer(B.R_POCKET + 0.3).difference(Point(*B.SPR).buffer(B.R_BOSS - 0.3)).union(Point(B.HOLE[0], B.HOLE[1]).buffer(B.HOLE[2] / 2 + 0.25))
CARD = box(0, 0, B.L, B.Wd)

def lines_of(g):
    if g.is_empty: return []
    if g.geom_type == "LineString": return [g]
    if g.geom_type in ("MultiLineString", "GeometryCollection"): return [x for h in g.geoms for x in lines_of(h)]
    return []

def face(name, svg, mirror):
    traces, fills = B.cam_geometry(svg, mirror)
    d = ezdxf.new("R2010", setup=False); d.units = 4; msp = d.modelspace(); stats = {}
    for depth, ls in traces.items():
        layer = "TRACE_%03d" % round(depth * 1000); d.layers.add(layer)
        merged = linemerge(MultiLineString([l for l in ls if l.length > 0])) if ls else MultiLineString([])
        clipped = lines_of(unary_union(lines_of(merged)).difference(KEEP).intersection(CARD)) if ls else []
        clipped = lines_of(linemerge(MultiLineString(clipped))) if clipped else []
        n = 0; length = 0.0
        for l in clipped:
            l = l.simplify(0.003)
            if l.length < 0.02: continue
            pts = list(l.coords); closed = pts[0] == pts[-1] and len(pts) > 3
            msp.add_lwpolyline(pts[:-1] if closed else pts, close=closed, dxfattribs={"layer": layer}); n += 1; length += l.length
        stats[layer] = (n, round(length))
    d.saveas(out / f"engraving_v3_{name}_traces.dxf")
    fills = fills.difference(KEEP).intersection(CARD)
    d = ezdxf.new("R2010", setup=False); d.units = 4; msp = d.modelspace(); k = 0
    for p in (fills.geoms if hasattr(fills, "geoms") else [fills]):
        p = p.simplify(0.008)
        if p.is_empty or p.area < 2e-4: continue
        for ring in [p.exterior, *p.interiors]:
            msp.add_lwpolyline(list(ring.coords)[:-1], close=True, dxfattribs={"layer": "0"}); k += 1
    d.saveas(out / f"engraving_v3_{name}_fills.dxf")
    import shapely
    widest = max((2 * shapely.maximum_inscribed_circle(g).length for g in (fills.geoms if hasattr(fills, "geoms") else [fills]) if g.area > 0.01), default=0)
    print(name, "traces", stats, "| fills: loops", k, "area %.1f mm2" % fills.area, "widest %.2f mm" % widest)

def helpers():
    d = ezdxf.new("R2010", setup=False); d.units = 4; msp = d.modelspace()
    for layer in ("OUTLINE", "FACE_AREA", "RECESS", "SLOTS", "CARD_HOLE", "REF_HOLES", "RIPPLE_AREA", "COMP_030", "COMP_015", "COMP_005"): d.layers.add(layer)
    L, Wd, r, b = B.L, B.Wd, B.R_CORNER, math.tan(math.pi / 8)
    msp.add_lwpolyline([(r, 0, 0), (L - r, 0, b), (L, r, 0), (L, Wd - r, b), (L - r, Wd, 0), (r, Wd, b), (0, Wd - r, 0), (0, r, b)], format="xyb", close=True, dxfattribs={"layer": "OUTLINE"})
    m = 4.0
    msp.add_lwpolyline([(-m, -m), (L + m, -m), (L + m, Wd + m), (-m, Wd + m)], close=True, dxfattribs={"layer": "FACE_AREA"})
    msp.add_circle(B.SPR, B.R_POCKET, dxfattribs={"layer": "RECESS"}); msp.add_circle(B.SPR, B.R_BOSS, dxfattribs={"layer": "RECESS"})
    for k in range(3):
        pts = []
        for i in range(121):
            a = math.radians(k * 120 - 90 + 205 * i / 120); rr = 6.2 + (11.8 - 6.2) * i / 120
            pts.append((B.SPR[0] + rr * math.cos(a), B.SPR[1] - rr * math.sin(a)))
        msp.add_lwpolyline(pts, dxfattribs={"layer": "SLOTS"})
    msp.add_circle((B.HOLE[0], B.HOLE[1]), B.HOLE[2] / 2, dxfattribs={"layer": "CARD_HOLE"})
    for sx in (-1, 1): msp.add_circle((L / 2 + sx * REF_X, Wd / 2), 1.5, dxfattribs={"layer": "REF_HOLES"})
    # ripple area: the recto above the name band, pushed out past the card edge so the ball runs off it
    msp.add_lwpolyline([(-1, B.BAND_Y + 0.25), (L + 1, B.BAND_Y + 0.25), (L + 1, Wd + 1), (-1, Wd + 1)], close=True, dxfattribs={"layer": "RIPPLE_AREA"})
    msp.add_circle(B.SPR, 13.9, dxfattribs={"layer": "RIPPLE_AREA"})
    # scallop comparator: parallel ball-nose passes inside each verso patch (verso view -> model x mirrored)
    sx0, sy0, sw, inset = 6.2, 41.0, 6.4, 0.45
    for i, (pitch, layer) in enumerate(((0.30, "COMP_030"), (0.15, "COMP_015"), (0.05, "COMP_005"))):
        u0 = sx0 + i * 8.6; n = int((sw - 2 * inset) / pitch) + 1; start = u0 + (sw - (n - 1) * pitch) / 2
        for k in range(n):
            u = start + k * pitch; ya, yb = sy0 + inset, sy0 + sw - inset
            if k % 2: ya, yb = yb, ya
            msp.add_line((L - u, Wd - ya * B.SY), (L - u, Wd - yb * B.SY), dxfattribs={"layer": layer})
    d.saveas(out / "cam_v3_helpers.dxf")

REF_X = 50.0     # reference holes sit this far left and right of the card centre, on its long axis
if __name__ == "__main__":
    body, _, recto, verso = B.build(engrave=False)
    print("body solids:", len(body.Solids()), "valid:", body.isValid(), "volume %.1f mm3" % body.Volume(), "T", B.T)
    cq.exporters.export(cq.Workplane(obj=body), str(out / "card_v3_body.step"))
    face("verso", B.G.back(), True); face("recto", B.G.front(), False); helpers()
