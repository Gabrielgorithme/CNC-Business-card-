"""Builds the 3D model of the card (STEP) from the same layout as the v2 mockup.

Card frame [mm]: X along the long edge, Y up, as seen from the RECTO. Z = 0 is the verso
face (datum A), Z = 2 the recto face. The verso artwork is mirrored in X so it reads
correctly when the card is flipped about its long axis... (flip about the Y axis).
"""
import sys, math, pathlib, functools
import numpy as np
import cadquery as cq
import svgelements as se
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "design" / "v2"))
import generate as G

L, Wd, T = 85.60, 53.98, 2.00          # card
R_CORNER, CHAMFER = 3.18, 0.15
SPR = (G.SPR[0], Wd - G.SPR[1])        # spring centre, card frame
R_POCKET, R_BOSS, WEB = 13.0, 4.8, 0.40
POCKET_DEPTH = (T - WEB) / 2           # 0.80 from each face
SLOT_W = 1.0
HOLE = (L - 5.0, Wd - 5.0, 3.0)        # x, y, diameter (5 mm from datums B/C seen from verso)
ENGRAVE_VERSO, ENGRAVE_RECTO = 0.10, 0.15
BAND_Y = Wd - G.BAND_Y
SY = Wd / 54.0                         # mockup is drawn 54.0 high
FD = "/usr/share/fonts/truetype/dejavu/"
FONTS = {("sans", False): FD + "DejaVuSansCondensed.ttf", ("sans", True): FD + "DejaVuSansCondensed-Bold.ttf",
         ("mono", False): FD + "DejaVuSansMono.ttf", ("mono", True): FD + "DejaVuSansMono-Bold.ttf"}
ENGRAVE_COLOURS = {G.ENG, G.ENG2, "#24282d", "#b9bdc3", "#5d646c"}

# ---------------------------------------------------------------- SVG -> 2D engraving regions
def colour(v):
    if v is None or getattr(v, "value", 1) is None: return None
    try: return se.Color(v).hex if not isinstance(v, se.Color) else v.hex
    except Exception: return None

@functools.lru_cache(maxsize=None)
def glyph(ch, fname):
    fp = FontProperties(fname=fname)
    ext = lambda t: TextPath((0, 0), t, size=1.0, prop=fp).get_extents()
    shape = None
    if ch.strip():
        for p in TextPath((0, 0), ch, size=1.0, prop=fp).to_polygons():
            if len(p) >= 3:
                q = Polygon(p).buffer(0); shape = q if shape is None else shape.symmetric_difference(q)
    adv = ext("|" + ch + "|").x1 - ext("||").x1
    return shape, adv

def text_shape(el):
    v = el.values
    size = float(v.get("font-size", 10)); ls = float(v.get("letter-spacing", 0) or 0)
    fam = "mono" if "Mono" in v.get("font-family", "") else "sans"
    fname = FONTS[(fam, int(float(v.get("font-weight", 400))) >= 600)]
    parts, x = [], 0.0
    for ch in el.text:
        shp, adv = glyph(ch, fname)
        if shp is not None and not shp.is_empty:
            parts.append(affinity.translate(affinity.scale(shp, size, -size, origin=(0, 0)), x, 0))
        x += adv * size + ls
    width = x - ls
    dx = {"start": 0, "middle": -width / 2, "end": -width}[v.get("text-anchor", "start")]
    g = affinity.translate(unary_union(parts), float(v.get("x", 0)) + dx, float(v.get("y", 0)))
    m = el.transform
    return affinity.affine_transform(g, [m.a, m.c, m.b, m.d, m.e, m.f])

def path_shape(el, stroke, fill):
    p = se.Path(el) if not isinstance(el, se.Path) else el
    p = abs(p)                                           # apply transforms
    out = []
    for sub in p.as_subpaths():
        sp = se.Path(sub)
        if len(sp) < 2: continue
        n = max(2, int(sp.length(error=1e-3) / 1.5) + 1)
        segs_curved = any(isinstance(s, (se.Arc, se.CubicBezier, se.QuadraticBezier)) for s in sp)
        if segs_curved: pts = [(pt.x, pt.y) for pt in (sp.point(i / (n * 4)) for i in range(n * 4 + 1))]
        else:
            pts = []
            for s in sp:
                if isinstance(s, se.Move): pts.append((s.end.x, s.end.y))
                elif isinstance(s, (se.Line, se.Close)) and s.end is not None: pts.append((s.end.x, s.end.y))
        pts = [q for i, q in enumerate(pts) if i == 0 or q != pts[i - 1]]
        if len(pts) < 2: continue
        if fill and len(pts) >= 3: out.append(Polygon(pts).buffer(0))
        if stroke:
            w = float(el.values.get("stroke-width", 1))
            out.append(LineString(pts).buffer(w / 2, cap_style=2, join_style=2))
    return unary_union(out) if out else None

def engraving(svg_text, mirror):
    """Union of everything engraved on one face, in card-frame mm."""
    import io
    doc = se.SVG.parse(io.StringIO(svg_text), reify=False)
    shapes = []
    for el in doc.elements():
        if isinstance(el, (se.SVG, se.Group, se.Image, se.ClipPath)) or not hasattr(el, "values"): continue
        v = el.values
        if v.get("clip-path") is None and v.get("filter"): continue
        stroke = v.get("stroke") in ENGRAVE_COLOURS
        fill = v.get("fill") in ENGRAVE_COLOURS
        if isinstance(el, se.Text):
            if v.get("fill") in ENGRAVE_COLOURS: shapes.append(text_shape(el))
        elif isinstance(el, se.Shape) and (stroke or fill):
            s = path_shape(el, stroke, fill)
            if s is not None: shapes.append(s)
    u = unary_union([s for s in shapes if s is not None and not s.is_empty])
    u = affinity.translate(u, -30, -30)                                      # undo the mock-up's viewBox margin
    u = affinity.affine_transform(u, [0.1, 0, 0, -0.1 * SY, 0, Wd])          # svg units -> mm, y up
    if mirror: u = affinity.affine_transform(u, [-1, 0, 0, 1, L, 0])
    return u

def to_solids(region, z0, z1):
    polys = [region] if isinstance(region, Polygon) else list(region.geoms)
    solids = []
    for p in polys:
        p = p.simplify(0.015)
        if p.is_empty or p.area < 1e-4: continue
        for q in ([p] if isinstance(p, Polygon) else p.geoms):
            mk = lambda ring: cq.Wire.makePolygon([cq.Vector(x, y, z0) for x, y in list(ring.coords)[:-1]], close=True)
            try:
                face = cq.Face.makeFromWires(mk(q.exterior), [mk(r) for r in q.interiors])
                solids.append(cq.Solid.extrudeLinear(face, cq.Vector(0, 0, z1 - z0)))
            except Exception as e:
                print("  skipped a sliver:", e)
    return solids

def cut_all(body, solids, chunk=150):
    for i in range(0, len(solids), chunk):
        body = body.cut(cq.Compound.makeCompound(solids[i:i + chunk]))
    return body

# ---------------------------------------------------------------- build
def build():
    card = (cq.Workplane("XY").box(L, Wd, T, centered=False).edges("|Z").fillet(R_CORNER)
            .faces("+Z or -Z").edges().chamfer(CHAMFER)).val()

    # ripple: the height field only depends on the distance to the spring centre -> a revolve
    r = np.arange(14.2, 71.0, 0.1)
    h = -G.AMP * (0.5 - 0.5 * np.cos(2 * np.pi * r / G.LAMBDA)) * np.clip((r - 14.2) / 1.5, 0, 1) * np.exp(-r / 60.0)
    pts = [(float(a), float(T + b)) for a, b in zip(r, h)]
    prof = (cq.Workplane("XZ").moveTo(*pts[0]).spline(pts[1:], includeCurrent=True)
            .lineTo(pts[-1][0], T + 1).lineTo(pts[0][0], T + 1).close())
    tool = prof.revolve(360, (0, 0, 0), (0, 1, 0)).val().translate(cq.Vector(SPR[0], SPR[1], 0))
    region = cq.Workplane("XY").box(L, Wd - BAND_Y, 4, centered=False).translate((0, BAND_Y, 0)).val()
    card = card.cut(tool.intersect(region))

    # spring: pocket from both faces, boss left full thickness, three spiral slots through the web
    ring = (cq.Workplane("XY").center(*SPR).circle(R_POCKET).circle(R_BOSS).extrude(POCKET_DEPTH)).val()
    card = card.cut(ring).cut(ring.translate(cq.Vector(0, 0, T - POCKET_DEPTH)))
    slots = []
    for k in range(3):
        sp = []
        for i in range(81):
            a = math.radians(k * 120 - 90 + 205 * i / 80); rr = 6.2 + (11.8 - 6.2) * i / 80
            sp.append((SPR[0] + rr * math.cos(a), SPR[1] - rr * math.sin(a)))
        slots.append(LineString(sp).buffer(SLOT_W / 2, resolution=12))
    card = cut_all(card, to_solids(unary_union(slots), POCKET_DEPTH - 0.1, T - POCKET_DEPTH + 0.1))

    # reamed hole
    card = card.cut(cq.Workplane("XY").center(HOLE[0], HOLE[1]).circle(HOLE[2] / 2).extrude(T).val())

    # engraving, both faces, kept out of the pocket and the hole
    keep_out = Point(*SPR).buffer(R_POCKET + 0.3).difference(Point(*SPR).buffer(R_BOSS - 0.3)).union(Point(HOLE[0], HOLE[1]).buffer(HOLE[2] / 2 + 0.25))
    outline = box(0, 0, L, Wd)
    recto = engraving(G.front(), mirror=False).difference(keep_out).intersection(outline)
    verso = engraving(G.back(), mirror=True).difference(keep_out).intersection(outline)
    print("recto engraving area %.1f mm2, verso %.1f mm2" % (recto.area, verso.area))
    body = card
    card = cut_all(card, to_solids(recto, T - ENGRAVE_RECTO, T + 0.5))
    card = cut_all(card, to_solids(verso, -0.5, ENGRAVE_VERSO))
    return body, card, recto, verso

def dxf(region, path):
    import ezdxf
    d = ezdxf.new("R2010", setup=False); d.units = 4; msp = d.modelspace()
    for p in (region.geoms if hasattr(region, "geoms") else [region]):
        for ring in [p.exterior, *p.interiors]:
            msp.add_lwpolyline(list(ring.coords)[:-1], close=True)
    d.saveas(path)

if __name__ == "__main__":
    out = pathlib.Path(__file__).parent
    body, card, recto, verso = build()
    print("valid:", card.isValid(), " volume %.1f mm3" % card.Volume(), " mass 7075 %.1f g" % (card.Volume() * 2.81e-3))
    bb = card.BoundingBox(); print("bbox", round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3))
    cq.exporters.export(cq.Workplane(obj=body), str(out / "card_v2_body.step"))          # machining geometry, no engraving
    cq.exporters.export(cq.Workplane(obj=card), str(out / "card_v2_engraved.step"))      # visual mock-up, engraving as 0.10/0.15 pockets
    cq.exporters.export(cq.Workplane(obj=card), str(out / "card_v2_engraved.stl"), tolerance=0.004, angularTolerance=0.08)
    dxf(recto, out / "engraving_recto.dxf")
    dxf(affinity.affine_transform(verso, [-1, 0, 0, 1, L, 0]), out / "engraving_verso_as_viewed.dxf")
