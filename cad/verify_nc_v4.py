"""Replays the posted card G-code (one file per operation) against the design geometry.
Z: every check is written with Z0 = raw stock top and the finished face at Z-0.15. The Z of the raw top in each setup's own
WCS is read from meta.json ('ztop') and subtracted first, and a setup whose Z0 is not on the raw top is reported.
Process as run: facing straight to Z-0.15 (no skim pass), holes and part-off stop exactly at the underside. OP1: x = X+42.8, y = 26.99-Y. OP2 and the pin-hole prep (op3): x = X+42.8, y = Y+26.99.
Process: OP1 parts off the card together with an ear carrying the second locating hole; OP2 trims the ear off."""
import re, math, sys, json, numpy as np, shapely, ezdxf, pathlib
from shapely.geometry import Point, box, LineString, MultiLineString, Polygon
from shapely.ops import unary_union
import build_card as B
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/Business Card/cam/check_v3")
HERE = pathlib.Path(__file__).parent
FACE = -0.15
META = json.loads((D / 'meta.json').read_text())

def moves(path, op, step=0.04):
    x = y = 0.0; z = 15.0; mode = 0; pts = []      # kind: 0 rapid with XY motion, 1 feed, 2 vertical rapid
    for line in open(path):
        line = re.sub(r"\(.*?\)", "", line).strip()
        if not line or "G28" in line or "G53" in line: continue
        for g in re.findall(r"G(\d+)", line):
            if int(g) in (0, 1, 2, 3): mode = int(g)
        w = {k: float(v) for k, v in re.findall(r"([XYZIJ])(-?\d*\.?\d+)", line)}
        if not any(k in w for k in "XYZ"): continue
        nx, ny, nz = w.get("X", x), w.get("Y", y), w.get("Z", z)
        if mode in (2, 3) and ("I" in w or "J" in w):
            cx, cy = x + w.get("I", 0), y + w.get("J", 0); r = math.hypot(x - cx, y - cy)
            a0 = math.atan2(y - cy, x - cx); a1 = math.atan2(ny - cy, nx - cx)
            if mode == 2 and a1 >= a0: a1 -= 2 * math.pi
            if mode == 3 and a1 <= a0: a1 += 2 * math.pi
            n = max(2, int(abs(a1 - a0) * r / step))
            for i in range(1, n + 1):
                a = a0 + (a1 - a0) * i / n; pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z + (nz - z) * i / n, 1))
        else:
            n = max(1, int(math.dist((x, y, z), (nx, ny, nz)) / step))
            for i in range(1, n + 1):
                pts.append((x + (nx - x) * i / n, y + (ny - y) * i / n, z + (nz - z) * i / n, 1 if mode else (2 if (nx, ny) == (x, y) else 0)))
        x, y, z = nx, ny, nz
    a = np.array(pts); m = META[op - 1]            # WCS -> model x/y from the setup's own coordinate system
    a[:, 2] -= m.get('ztop', 0.0)                  # Z measured from the raw stock top, whatever the setup's Z0 is
    X, Y = a[:, 0].copy(), a[:, 1].copy()
    a[:, 0] = m['origin'][0] + X * m['x'][0] + Y * m['y'][0]; a[:, 1] = m['origin'][1] + X * m['x'][1] + Y * m['y'][1]
    return a

def dxf_lines(name, layer):
    out = []
    for e in ezdxf.readfile(HERE / name).modelspace():
        if e.dxf.layer != layer: continue
        if e.dxftype() == "LWPOLYLINE":
            p = [(q[0], q[1]) for q in e.get_points("xy")]
            if e.closed: p.append(p[0])
            out.append(LineString(p))
        elif e.dxftype() == "LINE": out.append(LineString([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]))
    return unary_union(out)

OUTLINE = box(B.R_CORNER, 0, B.L - B.R_CORNER, B.Wd).union(box(0, B.R_CORNER, B.L, B.Wd - B.R_CORNER)).union(unary_union([Point(x, y).buffer(B.R_CORNER, 64) for x in (B.R_CORNER, B.L - B.R_CORNER) for y in (B.R_CORNER, B.Wd - B.R_CORNER)]))
SPR = Point(*B.SPR); ok_all = True
TOOLD = {o['file']: o['D'] for m in META for o in m['ops']}; TOOLRE = {o['file']: o['RE'] for m in META for o in m['ops']}; OPS = {o['file']: o for m in META for o in m['ops']}
EAR = Point(-2.2, B.Wd / 2); BLANK = OUTLINE.union(EAR.buffer(3.3, 64)); CARD_HOLE = Point(B.HOLE[0], B.HOLE[1])
def line(tag, name, good, msg):
    global ok_all; ok_all &= bool(good)
    print("%-7s %-34s %s  %s" % (tag, name, "OK  " if good else "FAIL", msg))
def cutpts(a, below=-0.0005): return a[(a[:, 2] < below) & (a[:, 3] == 1)]
def common(tag, a):
    bad = ((a[:, 3] == 0) & (a[:, 2] < 0.5)).sum()
    return bad == 0, "XY rapids lower than Z+0.5: %d" % bad

for op in (1, 2, 3):
    print('---', META[op - 1]['setup'], '| WCS origin in the model: x %.2f y %.2f z %.2f' % tuple(META[op - 1]['origin']), '| stock', [round(v, 2) for v in META[op - 1]['stock']])
    zt = META[op - 1].get('ztop', 0.0)
    line('setup', 'Z0 on the raw stock top', abs(zt) < 1e-6, 'raw top is at Z%+.3f in this WCS%s' % (zt, '' if abs(zt) < 1e-6 else ': the program only cuts the right depths if Z is zeroed %.2f mm %s the raw top (checks below are done from the raw top)' % (abs(zt), 'below' if zt > 0 else 'above')))
    for f in sorted(D.glob("op%d_*.nc" % op)):
        name = OPS[f.name]['name'] if f.name in OPS else f.name
        k = int(f.stem.split("_")[1]); a = moves(f, op); c = cutpts(a); r_ok, r_msg = common(f.stem, a); P = shapely.points(c[:, :2])
        if "Face" in name or "face" in name:
            line(f.stem, name, r_ok and abs(c[:, 2].min() - FACE) < 1e-6 and (BLANK if op == 1 else OUTLINE).buffer(-0.01).within(unary_union([Point(x, y).buffer(TOOLD[f.name] / 2 - TOOLRE[f.name], 8) for x, y in c[:, :2]])), ("Z %.3f, covers the whole " + ("card and ear" if op == 1 else "card") + "; %s") % (c[:, 2].min(), r_msg))
        elif "recess" in name:
            r = shapely.distance(SPR, P); line(f.stem, name, r_ok and r.min() > 5.795 and r.max() < 12.005 and abs(c[:, 2].min() + 0.80) < 1e-6, "tool centre r %.3f..%.3f, floor Z %.3f; %s" % (r.min(), r.max(), c[:, 2].min(), r_msg))
        elif "Holes" in name or "Pin hole" in name:
            cen = [CARD_HOLE, EAR] if "Holes" in name else [CARD_HOLE]
            r = np.min([shapely.distance(q, P) for q in cen], axis=0); line(f.stem, name, r_ok and abs(r.max() - 0.525) < 0.003 and c[:, 2].min() < -2.0 + 1e-4 and ("Pin hole" in name or c[:, 2].min() > -2.0 - 1e-4), "tool centre out to %.3f from the hole axis -> D%.2f, Z %.2f; %s" % (r.max(), 2 * r.max() + 2, c[:, 2].min(), r_msg))
        elif "Part off" in name or "Trim" in name:
            ref = BLANK if "Part off" in name else OUTLINE; want = 1.1 if "rough" in name else 1.0
            d = shapely.distance(ref, P); inside = shapely.contains(ref, P).sum(); bottom = -2.0 if op == 1 else -1.85; deep = c[c[:, 2] < bottom + 1e-4]      # at or below the underside of the plate / blank
            through = ref.boundary.difference(unary_union([Point(x, y).buffer(1.0 + (0.11 if "rough" in name else 0.01), 12) for x, y in deep[:, :2]])) if len(deep) else ref.boundary
            if "Part off" in name: through = through.difference(unary_union([Point(0, B.Wd / 2 + sg * 2.46).buffer(2.2) for sg in (-1, 1)]))   # the two inside corners where the ear meets the card: a round tool leaves fillets there, the OP2 trim removes them
            if "Trim" in name: through = LineString([(0, B.Wd / 2 - 4.2), (0, B.Wd / 2 + 4.2)]).difference(unary_union([Point(x, y).buffer(1.0 + (0.11 if "rough" in name else 0.01), 12) for x, y in deep[:, :2]]))
            line(f.stem, name, r_ok and inside == 0 and d.min() > want - 0.006 and through.length < 0.05 and c[:, 2].min() > bottom - 1e-4, "tool edge stays %.3f mm off the %s (wants %.1f), reaches the underside along all of it but %.2f mm, Z %.2f = %.2f below the underside; %s" % (d.min() - 1.0, "card + ear outline" if "Part off" in name else "card edge", want - 1.0, through.length, c[:, 2].min(), bottom - c[:, 2].min(), r_msg))
        elif "Engrave lines" in name:
            dep = float(re.search(r"lines (\d\.\d+)", name).group(1)); ref = dxf_lines("engraving_v3_%s_traces.dxf" % ("verso" if op == 1 else "recto"), "TRACE_%03d" % round(dep * 1000))
            atd = c[np.abs(c[:, 2] - (FACE - dep)) < 1e-4]; dist = shapely.distance(ref, shapely.points(atd[:, :2]))
            cov = ref.difference(unary_union([Point(x, y).buffer(0.03, 4) for x, y in atd[:, :2]]).buffer(0.01)).length
            deeper = (c[:, 2] < FACE - dep - 1e-4).sum()
            line(f.stem, name, r_ok and dist.max() < 0.012 and deeper == 0 and cov < 0.5, "Z %.3f, off the drawn line by at most %.3f, %.0f of %.0f mm traced, deeper points %d; %s" % (FACE - dep, dist.max(), ref.length - cov, ref.length, deeper, r_msg))
        elif "V-carve" in name:
            polys = [Polygon(l.coords) for l in dxf_lines("engraving_v3_verso_fills.dxf", "0").geoms]; art = polys[0]
            for q in polys[1:]: art = art.symmetric_difference(q)
            h = FACE - c[:, 2]; cc = c[h > 0.001]; h = h[h > 0.001]; PP = shapely.points(cc[:, :2])
            inside = shapely.contains(art.buffer(0.02), PP); over = np.where(inside, h - shapely.distance(art.boundary, PP), h)
            line(f.stem, name, r_ok and over.max() < 0.02, "V tip never leaves the fills; overcut at the finished face %.3f max; deepest %.2f below the face; %s" % (over.max(), h.max(), r_msg))
        elif "comparator" in name:
            ref = unary_union([dxf_lines("cam_v3_helpers.dxf", l) for l in ("COMP_030", "COMP_015", "COMP_005")]); atd = c[np.abs(c[:, 2] + 0.19) < 1e-4]
            dist = shapely.distance(ref, shapely.points(atd[:, :2])); line(f.stem, name, r_ok and dist.max() < 0.012 and c[:, 2].min() > -0.1905, "Z %.3f, on the pass lines within %.3f; %s" % (c[:, 2].min(), dist.max(), r_msg))
        elif "Chamfer" in name:
            cc = c[np.abs(c[:, 2] + 0.40) < 1e-4]; d = shapely.distance(OUTLINE, shapely.points(cc[:, :2])); ins = shapely.contains(OUTLINE, shapely.points(cc[:, :2])).sum()
            on = (np.abs(d - 0.1) < 0.006).mean()
            line(f.stem, name, r_ok and ins == 0 and abs(d.min() - 0.1) < 0.006 and on > 0.95, "tip 0.25 below the face and 0.100 outside the outline on %.0f%% of the pass (the rest is the lead moving away, to %.2f) -> chamfer %.3f wide; %s" % (100 * on, d.max(), 0.25 - d.min(), r_msg))
        elif "slots" in name:
            ref = dxf_lines("cam_v3_helpers.dxf", "SLOTS"); dist = shapely.distance(ref, P); lv = sorted(set(np.round(c[np.abs(np.diff(c[:, 2], prepend=0)) < 1e-9][:, 2], 2)))
            line(f.stem, name, r_ok and dist.max() < 0.012 and -1.85 + 0.05 < c[:, 2].min() < -1.20 - 0.03, "on the slot centrelines within %.3f, Z min %.2f: %.2f below the web (web is -0.80 to -1.20) and %.2f above the underside (-1.85); %s" % (dist.max(), c[:, 2].min(), -1.20 - c[:, 2].min(), c[:, 2].min() + 1.85, r_msg))
        elif "Ripples" in name:
            r = shapely.distance(SPR, P); surf = 1.85 * 0 + FACE - B.SKIM - B.G.AMP * (0.5 - 0.5 * np.cos(2 * np.pi * r / B.G.LAMBDA)) * np.clip((r - 14.2) / 1.5, 0, 1) * np.exp(-r / 60.0)
            interior = shapely.contains(OUTLINE.buffer(-1.7).difference(Point(B.HOLE[0], B.HOLE[1]).buffer(3.2)).intersection(box(0, B.BAND_Y + 1.8, B.L, B.Wd)).difference(SPR.buffer(15.8)), P)
            dz = c[interior, 2] - surf[interior]; low = c[c[:, 2] < FACE - 0.16]; pl = shapely.points(low[:, :2])
            where = "edge" if len(low) and shapely.distance(OUTLINE.boundary, pl).max() < 1.0 else "other"
            near_hole = (shapely.distance(Point(B.HOLE[0], B.HOLE[1]), pl) < 3.2).sum(); near_edge = (shapely.distance(OUTLINE.boundary, pl) < 0.5).sum(); near_recess = (shapely.distance(SPR, pl) < 15.5).sum(); near_band = (low[:, 1] < B.BAND_Y + 1.6).sum()
            inside_card = shapely.contains(OUTLINE.buffer(0.02), P).mean()
            line(f.stem, name, r_ok and dz.min() > -0.006 and dz.max() < 0.02, "ball tip vs designed surface (interior): %+.4f..%+.4f mm; Z %.3f..%.3f; %.1f%% of points inside the outline" % (dz.min(), dz.max(), c[:, 2].min(), c[:, 2].max(), 100 * inside_card))
            print("        points lower than the deepest ripple (%d): near card edge %d, near hole %d, near recess rim %d, near band %d, lowest Z %.3f" % (len(low), near_edge, near_hole, near_recess, near_band, low[:, 2].min() if len(low) else 0))
        elif OPS[f.name]["strategy"] == "deburr":
            h = FACE - c[:, 2]; r = shapely.distance(SPR, P); rh = shapely.distance(CARD_HOLE, P); dout = shapely.distance(OUTLINE.boundary, P)
            rim = np.abs(r - 13.0) < 1.0; boss = np.abs(r - 4.8) < 1.0; hole = rh < 1.6; other = ~(rim | boss | hole)
            w_rim = (h - (13.0 - r))[rim]; w_boss = (h - (r - 4.8))[boss]; w_hole = (h - (1.525 - rh))[hole]
            msg = "Z %.3f..%.3f; chamfer it leaves at the finished face: recess rim %s, boss %s, card hole (3.05) %s; points elsewhere %d (nearest to the card edge %.2f)" % (c[:, 2].min(), c[:, 2].max(),
                  ("%.2f..%.2f" % (w_rim.min(), w_rim.max())) if rim.any() else "none", ("%.2f..%.2f" % (w_boss.min(), w_boss.max())) if boss.any() else "none", ("%.2f..%.2f" % (w_hole.min(), w_hole.max())) if hole.any() else "none", other.sum(), dout.min())
            line(f.stem, name, r_ok and c[:, 2].min() > -0.79, msg + "; " + r_msg)
        else:
            line(f.stem, name, False, "no check written for this operation")
print("ALL OK" if ok_all else "SOMETHING FAILED")
