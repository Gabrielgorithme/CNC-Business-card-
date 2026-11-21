"""Exports what the Fusion CAM needs: the machining body and the engraving contours in MODEL coordinates."""
import pathlib, cadquery as cq, ezdxf
from shapely.geometry import box, Point
import build_card as B
out = pathlib.Path(__file__).parent
body, _, recto, verso = B.build(engrave=False)
print("solids:", len(body.Solids()), "valid:", body.isValid(), "volume %.1f" % body.Volume())
cq.exporters.export(cq.Workplane(obj=body), str(out / "card_v2_body.step"))
# verso contours for the V-carve: no comparator patches (those are surfaced with ball mills)
keep_out = Point(*B.SPR).buffer(B.R_POCKET + 0.3).difference(Point(*B.SPR).buffer(B.R_BOSS - 0.3)).union(Point(B.HOLE[0], B.HOLE[1]).buffer(B.HOLE[2] / 2 + 0.25))
v = B.engraving(B.G.back(), True, B.ENGRAVE_COLOURS - {"#b9bdc3"}).difference(keep_out).intersection(box(0, 0, B.L, B.Wd))
def dxf(region, path, tol):
    d = ezdxf.new("R2010", setup=False); d.units = 4; msp = d.modelspace(); n = 0; k = 0
    for p in region.geoms:
        p = p.simplify(tol)
        if p.is_empty or p.area < 2e-4: continue
        for q in ([p] if p.geom_type == "Polygon" else p.geoms):
            for ring in [q.exterior, *q.interiors]:
                pts = list(ring.coords)[:-1]; msp.add_lwpolyline(pts, close=True); n += len(pts); k += 1
    d.saveas(path); print(path.name, "loops", k, "vertices", n)
dxf(v, out / "engraving_verso_model.dxf", 0.008)
dxf(recto, out / "engraving_recto_model.dxf", 0.008)
import shapely
ws = [2 * shapely.maximum_inscribed_circle(g).length for g in v.geoms if g.area > 0.3]
print("widest engraved feature (inscribed circle dia): %.2f mm" % max(ws))
