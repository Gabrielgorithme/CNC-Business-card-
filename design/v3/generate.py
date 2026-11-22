"""Card v3: ripple face (recto) + dense technical face (verso), ISOCP single-line lettering.
10 SVG units = 1 mm. The ripple is a real height field (mm), shaded with numpy; the same
function can later be exported as the 3D-contouring surface for CAM."""
import math, base64, io, pathlib, sys
import numpy as np, segno
import lettering as LT
from PIL import Image
OUT = pathlib.Path(__file__).parent
W, H, R = 856, 540, 32
CARD_W, CARD_H = 85.6, 53.98
URL = "https://gabrielgorithme.github.io/CNC-Business-card-/"   # the portfolio page in docs/; 33 x 33 modules, scans on the machined test card
QR_CAPTION = "SCAN - PORTFOLIO"
ENG, ENG2, CUT = "#3f454c", "#6f767f", "#0f1113"
SANS = "font-family=\"'DejaVu Sans Condensed','DIN Alternate','Bahnschrift','Roboto Condensed',Arial,sans-serif\""
MONO = "font-family=\"'DejaVu Sans Mono','Menlo','Consolas',monospace\""
SPR = (59.0, 22.0)            # spring centre on the recto [mm]
LAMBDA, AMP = 2.0, 0.12       # ripple wavelength and amplitude [mm]
BAND_Y = 39.2                 # flat name band starts here [mm]
HOLE_D = 3.05                 # card hole as the CAM mills it [mm]; cad/build_card.py takes it from here
HOLE_FIT, HOLE_DEV = "Ø3 D11", ("+0.080", "+0.020")   # limits 3.020 / 3.080, mean 3.050 = HOLE_D

def ripple_height(x, y):
    """Height in mm (0 = original face, negative = cut)."""
    r = np.hypot(x - SPR[0], y - SPR[1])
    env = np.clip((r - 14.2) / 1.5, 0, 1) * np.exp(-r / 60.0)
    band = np.clip((BAND_Y - 0.6 - y) / 1.2, 0, 1)
    return -AMP * (0.5 - 0.5 * np.cos(2 * np.pi * r / LAMBDA)) * env * band

def shade(height_fn, px_per_mm=20, seed=1):
    nx, ny = int(CARD_W * px_per_mm), int(CARD_H * px_per_mm)
    x, y = np.meshgrid(np.arange(nx) / px_per_mm, np.arange(ny) / px_per_mm)
    h = height_fn(x, y) if height_fn else np.zeros_like(x)
    gy, gx = np.gradient(h * 2.6, 1 / px_per_mm)   # slopes exaggerated for legibility on screen
    n = np.dstack([-gx, -gy, np.ones_like(h)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array([-0.5, -0.62, 0.6]); L /= np.linalg.norm(L)
    Hv = L + np.array([0, 0, 1.0]); Hv /= np.linalg.norm(Hv)
    diff = np.clip(n @ L, 0, 1); spec = np.clip(n @ Hv, 0, 1) ** 60
    rng = np.random.default_rng(seed)
    brushed = np.repeat(rng.normal(0, 1, (ny, 1)), nx, axis=1) * 0.006 + rng.normal(0, 0.005, (ny, nx))
    sweep = 0.06 * np.cos((x * 0.9 + y * 1.4) / 14.0)          # soft studio reflection
    v = 0.40 + 0.52 * diff / L[2] * 0.66 + 0.55 * spec + brushed + sweep + h * 0.6
    v = np.clip(v, 0, 1)
    rgb = np.dstack([v * 0.965, v * 0.98, v * 1.0])
    img = Image.fromarray((rgb * 255).astype(np.uint8))
    buf = io.BytesIO(); img.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def T(x, y, s, size, weight=500, anchor="start", fill=ENG, ls=1.2, font=None, extra=""):
    """Single-line ISOCP text. `size` is the old font size in units (0.1 mm); the capital height it gave is kept,
    with Fusion's text height never below lettering.MIN_HEIGHT."""
    h = max(LT.MIN_HEIGHT, 0.729 * size / 10 / LT.CAP_RATIO)             # Fusion text height [mm]
    lines, width = LT.layout(s, h, ls * 0.035 * h / 0.7)
    dx = {"start": 0, "middle": -width / 2, "end": -width}[anchor]
    d = " ".join("M" + " L".join("%.2f,%.2f" % (x + (px + dx) * 10, y - py * 10) for px, py in ln) for ln in lines)
    sw = 20 * LT.depth_for(h * LT.CAP_RATIO)
    return f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{sw:g}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def P(d, w=1.3, stroke=ENG, fill="none", extra=""):
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{w}" fill="{fill}" {extra}/>'

def spiral(cx, cy, r0, r1, sweep, phase, flip=1, n=70):
    pts = []
    for i in range(n + 1):
        a = math.radians(phase + flip * sweep * i / n); r = r0 + (r1 - r0) * i / n
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return "M" + " L".join(pts)

def spring(cx, cy, flip=1, label=None):
    o = [f'<circle cx="{cx}" cy="{cy}" r="133" fill="#00000030"/>',
         f'<circle cx="{cx}" cy="{cy}" r="130" fill="url(#pocket)" stroke="#565c64" stroke-width="1.5"/>',
         f'<path d="M{cx-126},{cy-30} A130,130 0 0 1 {cx+30},{cy-126}" stroke="#2a2e33" stroke-width="5" fill="none" opacity=".35"/>']
    for k in range(3):
        d = spiral(cx, cy, 62, 118, 205, k*120 - 90, flip)
        o.append(f'<path d="{d}" fill="none" stroke="{CUT}" stroke-width="10" stroke-linecap="round"/>')
        o.append(f'<path d="{d}" fill="none" stroke="#e9ecef" stroke-width="1" opacity=".5" transform="translate(1.6,1.8)" stroke-linecap="round"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="48" fill="url(#boss)" stroke="#5d646c" stroke-width="1.2"/>')
    if label: o.append(T(cx, cy + 9, label, 26, 700, "middle", ls=2))
    return "\n".join(o)

DEFS = f'''<radialGradient id="pocket"><stop offset="0" stop-color="#aeb3b9"/><stop offset=".8" stop-color="#949aa1"/><stop offset="1" stop-color="#70767e"/></radialGradient>
<linearGradient id="boss" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6e8eb"/><stop offset="1" stop-color="#b4b9bf"/></linearGradient>
<filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-opacity=".6"/></filter>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>'''

def card(img, body):
    """img: shaded metal texture (data URI), or None for the plain vector artwork."""
    ground = f'<image href="{img}" xlink:href="{img}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="none"/>' if img else f'<rect width="{W}" height="{H}" fill="#d2d5d9"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-30 -30 {W+60} {H+60}">
<defs>{DEFS}</defs>
<rect width="{W}" height="{H}" rx="{R}" fill="#c9ccd0" filter="url(#sh)"/>
<g clip-path="url(#clip)">{ground}{body}</g>
<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="{R-1}" fill="none" stroke="#fafbfc" stroke-width="3" opacity=".75"/>
<rect x="0" y="0" width="{W}" height="{H}" rx="{R}" fill="none" stroke="#50565d" stroke-width="1" opacity=".6"/>
</svg>'''

# ------------------------------------------------------------------ recto
def front(texture=True):
    cx, cy = SPR[0]*10, SPR[1]*10
    b = [spring(cx, cy, 1, "GG")]
    b.append(P(f"M0,{BAND_Y*10} H{W}", 1.2, "#5d646c"))
    b.append(T(48, 462, "GABRIEL GHANEM", 46, 700, ls=6))
    b.append(T(50, 500, "MANUFACTURING ENGINEER", 16, 500, ls=5.2))
    b.append(T(W-48, 500, "GG-2027-001  ·  REV C", 12, 500, "end", ENG2, 2))
    return card(shade(ripple_height) if texture else None, "\n".join(b))

# ------------------------------------------------------------------ verso helpers
def gdt_symbol(kind, x, y):
    """Geometric characteristic symbols (ISO 1101), drawn in a 22 x 22 cell centred on (x, y)."""
    if kind == "flatness":   return P(f"M{x-8},{y+5} l5,-10 h11 l-5,10 z", 1.4)
    if kind == "position":   return P(f"M{x-10},{y} h20 M{x},{y-10} v20", 1.3) + f'<circle cx="{x}" cy="{y}" r="5.5" fill="none" stroke="{ENG}" stroke-width="1.4"/>'
    if kind == "profile":    return P(f"M{x-8},{y+4} a8,8 0 0 1 16,0 z", 1.4)
    if kind == "parallel":   return P(f"M{x-7},{y+7} l6,-14 M{x+1},{y+7} l6,-14", 1.5)
    if kind == "runout":     return P(f"M{x-6},{y+7} l12,-14 m0,0 l-6,1 m6,-1 l-1,6", 1.4)

def fcf(x, y, kind, tol, datums=(), h=24):
    """Feature control frame. Returns (svg, total width)."""
    cells = [26, 14 + 8.6 * len(tol)] + [24] * len(datums)
    o, cx = [], x
    for i, wc in enumerate(cells):
        o.append(f'<rect x="{cx}" y="{y}" width="{wc}" height="{h}" fill="none" stroke="{ENG}" stroke-width="1.4"/>')
        if i == 0: o.append(gdt_symbol(kind, cx + wc/2, y + h/2))
        elif i == 1: o.append(T(cx + wc/2, y + 17, tol, 14, 600, "middle", ls=.4))
        else: o.append(T(cx + wc/2, y + 17, datums[i-2], 14, 700, "middle", ls=0))
        cx += wc
    return "\n".join(o), cx - x

def datum(x, y, letter, direction="up"):
    """Datum feature indicator: filled triangle on the feature, stem, boxed letter."""
    if direction == "up":     # triangle base on a bottom edge at y, symbol above
        return (P(f"M{x-7},{y} h14 l-7,-11 z", 1, fill=ENG) + P(f"M{x},{y-11} v-13") +
                f'<rect x="{x-11}" y="{y-46}" width="22" height="22" fill="none" stroke="{ENG}" stroke-width="1.4"/>' + T(x, y-29, letter, 15, 700, "middle", ls=0))
    if direction == "right":  # triangle base on a left edge at x, symbol to the right
        return (P(f"M{x},{y-7} v14 l11,-7 z", 1, fill=ENG) + P(f"M{x+11},{y} h13") +
                f'<rect x="{x+24}" y="{y-11}" width="22" height="22" fill="none" stroke="{ENG}" stroke-width="1.4"/>' + T(x+35, y+6, letter, 15, 700, "middle", ls=0))

def basic(x, y, s):   # theoretically exact dimension (boxed)
    w = 12 + 8 * len(s)
    return f'<rect x="{x-w/2}" y="{y-10}" width="{w}" height="19" fill="none" stroke="{ENG}" stroke-width="1.2"/>' + T(x, y+5, s, 13, 600, "middle", ls=0)

def arrow(x, y, ang):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    p = lambda dx, dy: f"{x + dx*c - dy*s:.1f},{y + dx*s + dy*c:.1f}"
    return f'<path d="M{x},{y} L{p(-11,-3.4)} L{p(-11,3.4)} z" fill="{ENG}"/>'

def qr(x, y, size):
    m = [list(r) for r in segno.make(URL, error="m").matrix]
    n = len(m); c = size / n
    o = [f'<rect x="{x-9}" y="{y-9}" width="{size+18}" height="{size+18}" rx="5" fill="#eceef1" stroke="{ENG2}" stroke-width="1"/>']
    for j, row in enumerate(m):
        for i, v in enumerate(row):
            if v: o.append(f'<rect x="{x+i*c:.2f}" y="{y+j*c:.2f}" width="{c+.3:.2f}" height="{c+.3:.2f}" fill="#24282d"/>')
    return "\n".join(o)

SN = [(1e4, 380), (1e5, 300), (1e6, 230), (1e7, 185), (1e8, 165), (5e8, 159)]   # 7075-T6, R=-1, approx.

def back(texture=True):
    b = []
    cx, cy = W - SPR[0]*10, SPR[1]*10            # mirrored: (266, 220)
    # --- mm rulers on two edges
    for i in range(0, 86):
        hh = 15 if i % 10 == 0 else 10 if i % 5 == 0 else 6
        b.append(P(f"M{i*10},{H} v{-hh}", 1))
        if i % 10 == 0 and 0 < i < 85: b.append(T(i*10 + 3, H - 17, str(i), 9, 600, ls=0))
    # --- spring + centre marks + callouts
    b.append(spring(cx, cy, -1))
    b.append(P(f"M{cx-148},{cy} H{cx+148} M{cx},{cy-148} V{cy+148}", 1, ENG2, extra='stroke-dasharray="16 4 3 4"'))
    b.append(P(f"M{cx-92},{cy+92} L128,362 H34", 1.2)); b.append(arrow(cx-92, cy+92, -47))
    b.append(T(36, 356, "Ø26 ±0.05", 14, 600))
    # leader from a leg to the web note
    b.append(P(f"M{cx+70},{cy-66} L{cx+142},{cy-162} h18", 1.2)); b.append(f'<circle cx="{cx+70}" cy="{cy-66}" r="3" fill="{ENG}"/>')
    b.append(T(cx+164, cy-164, "3× FLEXURE LEG", 12, 700, ls=1.6))
    b.append(T(cx+164, cy-148, "WEB 0.40 ±0.02", 13, 600))
    s, w_ = fcf(cx+164, cy-140, "profile", "0.05", ("A",)); b.append(s)
    # --- locating hole for the flip: milled (helical, 2 mm end mill) to 3.05 for a 3 mm pin.
    # ISO 286: D11 on a nominal 3 is +0.080/+0.020, i.e. 3.020 to 3.080, centred on the 3.05 the CAM cuts.
    hx, hy = 50, 50
    hr = HOLE_D * 5                                # drawn radius [units]
    b.append(f'<circle cx="{hx}" cy="{hy}" r="{hr:g}" fill="{CUT}" stroke="#30353a" stroke-width="1.5"/><circle cx="{hx}" cy="{hy}" r="{hr + 2.5:g}" fill="none" stroke="#f1f3f5" stroke-width="1.2" opacity=".8"/>')
    b.append(P(f"M{hx-24},{hy} h48 M{hx},{hy-24} v48", .9, ENG2, extra='stroke-dasharray="9 3 2 3"'))
    b.append(P(f"M{hx+11},{hy-11} L{hx+34},{hy-30} h14", 1.2)); b.append(arrow(hx+11, hy-11, 140))
    b.append(T(hx+52, hy-25, HOLE_FIT, 15, 700)); b.append(T(hx+110, hy-30, HOLE_DEV[0], 9, 600, ls=.3)); b.append(T(hx+110, hy-20, HOLE_DEV[1], 9, 600, ls=.3))
    s, w_ = fcf(hx+52, hy-16, "position", "Ø0.05", ("A", "B", "C")); b.append(s)
    b.append(P(f"M{hx},{hy+26} v62 M0,{hy+78} h{hx}", 1)); b.append(arrow(hx, hy+78, 0)); b.append(basic(hx+22, hy+78, "5"))
    # --- datums: A (this face, via the flatness frame), B (long edge), C (short edge)
    b.append(datum(556, H, "B", "up")); b.append(datum(0, 400, "C", "right"))
    fx, fy = 420, 292
    s, w_ = fcf(fx, fy, "flatness", "0.05"); b.append(s)
    b.append(P(f"M{fx},{fy+12} h-18 l-22,22", 1.2)); b.append(f'<circle cx="{fx-40}" cy="{fy+34}" r="3.2" fill="{ENG}"/>')
    b.append(P(f"M{fx+w_/2},{fy+24} v12", 1.3) + P(f"M{fx+w_/2-7},{fy+36} h14 l-7,11 z", 1, fill=ENG) + P(f"M{fx+w_/2},{fy+47} v6"))
    b.append(f'<rect x="{fx+w_/2-11}" y="{fy+53}" width="22" height="22" fill="none" stroke="{ENG}" stroke-width="1.4"/>' + T(fx+w_/2, fy+70, "A", 15, 700, "middle", ls=0))
    # --- surface texture symbol
    rx, ry = 506, 352
    b.append(P(f"M{rx},{ry-12} l7,12 l14,-24 h44 M{rx},{ry-12} h14", 1.4)); b.append(T(rx+24, ry-2, "Ra 0.8", 12, 600, ls=.6))
    # --- G-code excerpt
    gx, gy = 420, 140
    for i, ln in enumerate(["%", "O2027 (GG CARD OP2)", "G21 G90 G17 G54", "T405 M6 (D1 2FL)", "S24000 M3", "G0 X26.6 Y15.8", "G1 Z-1.25 F120", "G3 X38.4 Y22. I-6.1", "   J9.4 F480", "(... 2847 BLOCKS)"]):
        b.append(T(gx, gy + i*12.6, ln, 9.2, 500, fill=ENG if i else ENG2, ls=0, font=MONO))
    # --- QR
    qx, qy, qs = 594, 50, 222
    b.append(qr(qx, qy, qs))
    b.append(T(qx+qs/2, qy+qs+31, QR_CAPTION, 12, 700, "middle", ls=3))
    # first-angle projection symbol + standards note
    px, py = 598, 322
    b.append(P(f"M{px},{py} l26,-6 v26 l-26,-6 z", 1.3)); b.append(f'<circle cx="{px+48}" cy="{py+7}" r="13" fill="none" stroke="{ENG}" stroke-width="1.3"/><circle cx="{px+48}" cy="{py+7}" r="7" fill="none" stroke="{ENG}" stroke-width="1.3"/>')
    b.append(P(f"M{px-6},{py+7} h76", .8, ENG2, extra='stroke-dasharray="9 3 2 3"'))
    b.append(T(px+78, py+3, "ISO 8015  ·  ISO 2768-fH", 10.5, 600, ls=1)); b.append(T(px+78, py+17, "AL 7075-T6  ·  ≈ 19.5 g", 10.5, 600, ls=1))
    # --- scallop comparator: three ball-nose patches
    sx, sy, sw = 62, 410, 64
    b.append(T(sx, sy-10, "SCALLOP COMPARATOR · R1.5 BALL · h = s·s/8R", 9, 700, ls=.5))
    for i, (step, hgt) in enumerate([("0.30", "7.5 µm"), ("0.15", "1.9 µm"), ("0.05", "0.2 µm")]):
        x0 = sx + i*(sw+22)
        b.append(f'<rect x="{x0}" y="{sy}" width="{sw}" height="{sw}" fill="#b9bdc3" stroke="{ENG}" stroke-width="1.2"/>')
        pitch = float(step) * 10; k = 0
        while k * pitch < sw - .5:
            b.append(P(f"M{x0 + k*pitch + pitch/2:.2f},{sy+1} v{sw-2}", max(.35, pitch*.42), "#7b828a", extra='opacity=".85"')); k += 1
        b.append(T(x0 + sw/2, sy+sw+13, "s " + step, 10, 700, "middle", ls=.4)); b.append(T(x0 + sw/2, sy+sw+25, hgt, 9.5, 500, "middle", ENG2, ls=.3))
    # --- S-N curve
    ox, oy, gw, gh = 346, 474, 170, 80
    X = lambda n: ox + (math.log10(n) - 4) / (math.log10(5e8) - 4) * gw
    Y = lambda sg: oy - sg / 400 * gh
    b.append(P(f"M{ox},{oy-gh-6} V{oy} H{ox+gw+6}", 1.3))
    for e in range(4, 9): b.append(P(f"M{X(10**e):.1f},{oy} v4", 1)); b.append(T(X(10**e), oy+14, f"1E{e}", 8.5, 500, "middle", ls=0))
    for sg in (100, 200, 300, 400): b.append(P(f"M{ox-4},{Y(sg):.1f} h4", 1)); b.append(T(ox-7, Y(sg)+3, str(sg), 8.5, 500, "end", ls=0))
    b.append(P("M" + " L".join(f"{X(n):.1f},{Y(sg):.1f}" for n, sg in SN), 1.8))
    b.append(P(f"M{ox},{Y(134):.1f} H{ox+gw}", 1, ENG, extra='stroke-dasharray="5 3"'))
    b.append(f'<circle cx="{X(5e8):.1f}" cy="{Y(134):.1f}" r="3.6" fill="{ENG}"/>')
    b.append(T(ox+8, Y(134)+13, "THIS SPRING: 134 MPa @ ±1 mm", 8.8, 700, ls=.4))
    b.append(T(ox+gw, oy-gh-2, "S-N  7075-T6  R=-1  [MPa]", 8.8, 600, "end", ls=.3))
    b.append(T(ox+gw+2, oy-gh+12, "S = Kt·3·E·t·d / (L·L)", 10.5, 600, "end", ls=.3, font=MONO))
    # --- text block
    tx = 584
    b.append(T(tx, 384, "DESIGNED, PROGRAMMED", 12.5, 700, ls=1)); b.append(T(tx, 404, "AND MACHINED BY THE PERSON", 12.5, 700, ls=1)); b.append(T(tx, 424, "WHO HANDED IT TO YOU.", 12.5, 700, ls=1))
    b.append(P(f"M{tx},437 H{W-40}", 1))
    b.append(T(tx, 456, "+33 6 60 45 50 18", 12.5, 600, ls=1.4)); b.append(T(tx, 473, "GABRIEL.GHANEM@GMAIL.COM", 12, 600, ls=1))
    b.append(T(tx, 496, "AVAILABLE SEPT. 2027", 12.5, 700, ls=1.4)); b.append(T(W-40, 496, "03 / 12", 12.5, 700, "end", ls=1.4))
    # --- rocket easter egg + micro text
    b.append(f'<g transform="translate(78,332) rotate(-90) scale(.8)">' + P("M230,0 c-14,-9 -30,-13 -46,-13 h-150 l-18,-12 v12 h-8 v26 h8 v12 l18,-12 h150 c16,0 32,-4 46,-13 z M184,-13 v26 M34,-13 v26", 1.1)
             + T(40, 3.2, "LÉOFLY · TECH. DIRECTOR", 8.2, 700, ls=.5) + "</g>")
    b.append(f'<g transform="translate({W-9},{H-46}) rotate(-90)">' + T(0, 0, "IF YOU CAN READ THIS, THE ENGRAVING BIT WAS SHARP · NO LASER WAS USED ON THIS CARD", 6.4, fill=ENG2, ls=1.1) + "</g>")
    return card(shade(None, seed=7) if texture else None, "\n".join(b))

if __name__ == "__main__":
    # v3_*.svg carry the shaded metal texture and are only the source of the PNG mockups (render_png.cjs); they are not committed.
    # v3_*_artwork.svg are the same drawing on a flat ground: pure vectors, what the CAM inputs are derived from.
    for name, fn in (("front", front), ("back", back)):
        (OUT / f"v3_{name}.svg").write_text(fn(), encoding="utf-8")
        (OUT / f"v3_{name}_artwork.svg").write_text(fn(texture=False), encoding="utf-8")
