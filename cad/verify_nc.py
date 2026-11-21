"""Independent check of the posted verso G-code against the design geometry.
Simulates linear and arc moves, maps WCS -> card frame (x = X + 42.8, y = 26.99 - Y, depth = -Z)."""
import re, sys, math, numpy as np, shapely
from shapely.geometry import Point, box, MultiPoint
import build_card as B

def moves(path, step=0.05):
    x = y = 0.0; z = 15.0; mode = 0; pts = []    # (x, y, z, kind): 0 = rapid with XY motion, 1 = feed, 2 = vertical rapid
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
                a = a0 + (a1 - a0) * i / n
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z + (nz - z) * i / n, 1))
        else:
            n = max(1, int(math.dist((x, y, z), (nx, ny, nz)) / step))
            for i in range(1, n + 1):
                pts.append((x + (nx - x) * i / n, y + (ny - y) * i / n, z + (nz - z) * i / n, 1 if mode else (2 if (nx, ny) == (x, y) else 0)))
        x, y, z = nx, ny, nz
    a = np.array(pts); a[:, 0] += 42.8; a[:, 1] = 26.99 - a[:, 1]
    return a

d = "/mnt/user-data/uploads/Business Card/cam/check/"
# --- engraving (90 deg V): at depth h the tool cuts a disc of radius h; it must stay inside the artwork
keep_out = Point(*B.SPR).buffer(B.R_POCKET + 0.3).difference(Point(*B.SPR).buffer(B.R_BOSS - 0.3)).union(Point(B.HOLE[0], B.HOLE[1]).buffer(B.HOLE[2] / 2 + 0.25))
art = B.engraving(B.G.back(), True, B.ENGRAVE_COLOURS - {"#b9bdc3"}).difference(keep_out).intersection(box(0, 0, B.L, B.Wd))
a = moves(d + "check_op3.nc"); cut = a[a[:, 2] < -0.001]
print("ENGRAVE: %d sampled cutting points, depth max %.3f, XY XY rapids below Z0: %d" % (len(cut), -cut[:, 2].min(), ((a[:, 3] == 0) & (a[:, 2] < 0)).sum()))
P = shapely.points(cut[:, :2]); inside = shapely.contains(art.buffer(0.02), P)
dist = shapely.distance(art.boundary, P); over = np.where(inside, -cut[:, 2] - dist, -cut[:, 2])
print("  tool axis outside the artwork: %d points (%.2f %%)" % ((~inside).sum(), 100 * (~inside).mean()))
print("  overcut beyond the artwork edge (depth - distance to edge): max %.3f mm, 99.9th pct %.3f mm" % (over.max(), np.percentile(over, 99.9)))
cov = shapely.unary_union([Point(x, y).buffer(-z, 8) for x, y, z, _ in cut[::3]])
print("  artwork area %.1f mm2, area swept by the V at the surface %.1f mm2, swept outside artwork %.2f mm2, artwork left uncut %.2f mm2" % (art.area, cov.area, cov.difference(art.buffer(0.03)).area, art.difference(cov.buffer(0.03)).area))
deep = cut[cut[:, 2] < -0.6]
print("  points deeper than 0.6 mm: %d, x range %.1f-%.1f, y range %.1f-%.1f (QR spans x %.1f-%.1f)" % (len(deep), deep[:, 0].min(), deep[:, 0].max(), deep[:, 1].min(), deep[:, 1].max(), B.L - 81.6, B.L - 59.4))
# --- pocket and bore
for f, name, cx, cy in (("check_op1.nc", "POCKET", *B.SPR), ("check_op2.nc", "BORE", B.HOLE[0], B.HOLE[1])):
    a = moves(d + f); cut = a[a[:, 2] < -0.001]; r = np.hypot(cut[:, 0] - cx, cut[:, 1] - cy)
    print("%s: tool-centre radius %.3f..%.3f mm about its axis, Z min %.3f, XY rapids below Z0: %d" % (name, r.min(), r.max(), cut[:, 2].min(), ((a[:, 3] == 0) & (a[:, 2] < 0)).sum()))
