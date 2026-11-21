"""Generates the concept mockups (SVG, 10 units = 1 mm). Card: ISO ID-1, 85.6 x 53.98 x 2 mm."""
import math, segno, pathlib
OUT = pathlib.Path(__file__).parent
W, H, R = 856, 540, 32
URL = "https://gabrielgorithme.github.io/CNC-Business-card-/"   # placeholder target, to be shortened
ENG, ENG2, CUT = "#4d535b", "#7d848d", "#111315"
FONT = "font-family=\"'DIN Alternate','Bahnschrift','Roboto Condensed','Helvetica Neue',Arial,sans-serif\""

def spiral(cx, cy, r0, r1, sweep, phase, n=60, flip=1):
    pts = []
    for i in range(n + 1):
        a = math.radians(phase + flip * sweep * i / n)
        r = r0 + (r1 - r0) * i / n
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return "M" + " L".join(pts)

def spring(cx, cy, mode="part", flip=1, s=1.0):
    """Orthoplanar spring: 26 mm pocket, 3 spiral through-slots, 11 mm platform."""
    o = []
    rp, r0, r1 = 130*s, 62*s, 118*s
    if mode == "part":
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rp}" fill="url(#pocket)" stroke="{ENG}" stroke-width="1.5"/>')
        for k in range(3):
            o.append(f'<path d="{spiral(cx,cy,r0,r1,205,k*120-90,flip=flip)}" fill="none" stroke="{CUT}" stroke-width="{10*s}" stroke-linecap="round"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{48*s}" fill="url(#alu)" stroke="{ENG2}" stroke-width="1"/>')
    elif mode == "sketch":
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rp}" fill="none" stroke="{ENG}" stroke-width="1.6"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{48*s}" fill="none" stroke="{ENG}" stroke-width="1.6"/>')
        for k in range(3):
            o.append(f'<path d="{spiral(cx,cy,r0,r1,205,k*120-90,flip=flip)}" fill="none" stroke="{ENG}" stroke-width="{10*s}" stroke-linecap="round"/>')
            o.append(f'<path d="{spiral(cx,cy,r0,r1,205,k*120-90,flip=flip)}" fill="none" stroke="url(#alu)" stroke-width="{10*s-3}" stroke-linecap="round"/>')
        o.append(f'<path d="M{cx-rp-14},{cy} H{cx+rp+14} M{cx},{cy-rp-14} V{cy+rp+14}" stroke="{ENG2}" stroke-width="1" stroke-dasharray="14 4 3 4"/>')
    elif mode == "toolpath":
        for j in range(9):
            o.append(f'<circle cx="{cx}" cy="{cy}" r="{rp - j*9*s:.1f}" fill="none" stroke="{ENG2}" stroke-width="1"/>')
        for k in range(3):
            o.append(f'<path d="{spiral(cx,cy,r0,r1,205,k*120-90,flip=flip)}" fill="none" stroke="{ENG}" stroke-width="2.2"/>')
            a = math.radians(k*120-90)
            o.append(f'<path d="M{cx},{cy-rp-22} L{cx + r0*math.cos(a):.1f},{cy + r0*math.sin(a):.1f}" stroke="{ENG2}" stroke-width="1" stroke-dasharray="5 4"/>')
        o.append(f'<circle cx="{cx}" cy="{cy-rp-22}" r="4" fill="{ENG}"/>')
    return "\n".join(o)

def qr(x, y, size):
    q = segno.make(URL, error="m")
    m = [list(r) for r in q.matrix]
    n = len(m); c = size / n
    o = [f'<rect x="{x-8}" y="{y-8}" width="{size+16}" height="{size+16}" rx="6" fill="#e9ebee" stroke="{ENG2}" stroke-width="1"/>']
    for j, row in enumerate(m):
        for i, v in enumerate(row):
            if v: o.append(f'<rect x="{x+i*c:.2f}" y="{y+j*c:.2f}" width="{c+.3:.2f}" height="{c+.3:.2f}" fill="#2b2f34"/>')
    return "\n".join(o), n

def text(x, y, s, size, weight=500, anchor="start", fill=ENG, ls=1.5):
    return f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" letter-spacing="{ls}">{s}</text>'

def card(body, extra_defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-30 -30 {W+60} {H+60}">
<defs>
<linearGradient id="alu" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}"><stop offset="0" stop-color="#e3e5e8"/><stop offset=".45" stop-color="#c3c7cc"/><stop offset=".55" stop-color="#d4d7db"/><stop offset="1" stop-color="#a9aeb5"/></linearGradient>
<radialGradient id="pocket"><stop offset="0" stop-color="#b9bdc3"/><stop offset=".85" stop-color="#9da2a9"/><stop offset="1" stop-color="#7f858d"/></radialGradient>
<filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-opacity=".55"/></filter>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>
{extra_defs}</defs>
<rect width="{W}" height="{H}" rx="{R}" fill="url(#alu)" filter="url(#sh)"/>
<g clip-path="url(#clip)">{body}</g>
<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="{R-1}" fill="none" stroke="#f4f5f6" stroke-width="3" opacity=".7"/>
</svg>'''

TAG1, TAG2 = "DESIGNED, PROGRAMMED AND MACHINED", "BY THE PERSON WHO HANDED IT TO YOU."
PHONE, MAIL = "+33 6 60 45 50 18", "EMAIL — TO CONFIRM"

# ---------- A : the card is its own engineering drawing ----------
def a_front():
    b = [f'<rect x="22" y="22" width="{W-44}" height="{H-44}" fill="none" stroke="{ENG}" stroke-width="1.6"/>']
    for i, ch in enumerate("ABCD"):
        b.append(text(12, 95 + i*120, ch, 11, anchor="middle", ls=0))
    for i in range(1, 7):
        b.append(text(22 + (i-.5)*(W-44)/6, 17, str(i), 11, anchor="middle", ls=0))
        if i < 6: b.append(f'<path d="M{22+i*(W-44)/6:.0f},10 v12" stroke="{ENG}" stroke-width="1"/>')
    cx, cy = 200, 250
    b.append(spring(cx, cy))
    b.append(f'<path d="M{cx-150},{cy} H{cx+150} M{cx},{cy-150} V{cy+150}" stroke="{ENG2}" stroke-width="1" stroke-dasharray="14 4 3 4"/>')
    b.append(f'<path d="M{cx-130},{cy+150} V{cy+185} M{cx+130},{cy+150} V{cy+185} M{cx-130},{cy+176} H{cx+130}" stroke="{ENG}" stroke-width="1.2" fill="none"/>')
    b.append(f'<path d="M{cx-130},{cy+176} l12,-4 v8z M{cx+130},{cy+176} l-12,-4 v8z" fill="{ENG}"/>')
    b.append(text(cx, cy+200, "Ø26 ±0.05", 15, anchor="middle"))
    b.append(text(cx-150, cy-158, "A", 16, 700)); b.append(text(cx+140, cy-158, "A", 16, 700))
    # section A-A
    sx, sy = 400, 120
    b.append(f'<rect x="{sx}" y="{sy}" width="60" height="20" fill="{ENG2}"/><rect x="{sx+60}" y="{sy+8}" width="260" height="4" fill="{ENG}"/><rect x="{sx+150}" y="{sy+8}" width="80" height="4" fill="{ENG}"/><rect x="{sx+320}" y="{sy}" width="60" height="20" fill="{ENG2}"/>')
    b.append(text(sx+190, sy-14, "SECTION A–A  (5:1)", 13, anchor="middle"))
    b.append(text(sx+190, sy+42, "WEB 0.40 — 3 LEGS — ±1 mm TRAVEL", 12, anchor="middle"))
    b.append(text(sx, sy+72, "σ ≤ 134 MPa  ·  N &gt; 5×10⁸ CYCLES", 13, 700))
    # title block
    tx, ty, tw, th = 400, 300, W-22-400, H-22-300
    b.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="none" stroke="{ENG}" stroke-width="1.6"/>')
    b.append(f'<path d="M{tx},{ty+92} h{tw} M{tx},{ty+140} h{tw} M{tx},{ty+180} h{tw} M{tx+150},{ty+92} v{th-92} M{tx+300},{ty+92} v{th-92}" stroke="{ENG}" stroke-width="1.2" fill="none"/>')
    b.append(text(tx+10, ty+16, "DRAWN · PROGRAMMED · MACHINED BY", 10))
    b.append(text(tx+10, ty+56, "GABRIEL GHANEM", 38, 700, ls=3))
    b.append(text(tx+10, ty+80, "MANUFACTURING ENGINEER", 16, ls=3.2))
    cells = [("MATERIAL", "AL 7075-T6"), ("PART No", "GG-2027-001"), ("REV", "C"),
             ("PROCESS", "3-AXIS CNC"), ("SERIAL", "03 / 12"), ("SCALE", "1:1"),
             ("AVAILABLE", "SEPT. 2027"), ("TOL.", "ISO 2768-f"), ("SHEET", "1 / 2")]
    for i, (k, v) in enumerate(cells):
        x = tx + 10 + (i % 3)*150; y = ty + [92, 140, 180][i//3]
        b.append(text(x, y+13, k, 9, fill=ENG2)); b.append(text(x, y+33 if i < 3 else y+31, v, 16 if i < 3 else 14, 600))
    return card("\n".join(b))

def a_back():
    b = [f'<rect x="22" y="22" width="{W-44}" height="{H-44}" fill="none" stroke="{ENG}" stroke-width="1.6"/>']
    cx = W - 200
    b.append(spring(cx, 250, flip=-1))
    q, n = qr(70, 70, 250); b.append(q)
    b.append(text(70, 350, "SHEET 2 / 2 — DIGITAL TWIN", 13, 700))
    b.append(text(70, 372, "CAD MODEL · TOOLPATHS · MACHINING VIDEO", 11))
    b.append(text(70, 430, TAG1, 15, 600, ls=2)); b.append(text(70, 452, TAG2, 15, 600, ls=2))
    b.append(text(70, 496, PHONE + "   ·   " + MAIL, 13))
    for i in range(0, 81):  # mm ruler along bottom edge
        h = 16 if i % 10 == 0 else 11 if i % 5 == 0 else 6
        b.append(f'<path d="M{28+i*10},{H} v{-h}" stroke="{ENG}" stroke-width="1"/>')
    return card("\n".join(b))

# ---------- B : ripple — 3D-contoured waves radiating from the spring ----------
def ripples(cx, cy):
    o = []
    for i, r in enumerate(range(150, 1000, 14)):
        op = max(.12, .85 - i*.013)
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#6d737b" stroke-width="2.4" opacity="{op:.2f}"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r+4}" fill="none" stroke="#f7f8f9" stroke-width="2" opacity="{op*.8:.2f}"/>')
    return "\n".join(o)

def b_front():
    cx, cy = 590, 220
    b = [ripples(cx, cy), spring(cx, cy)]
    b.append(text(cx, cy+7, "GG", 26, 700, anchor="middle", ls=2))
    b.append(f'<rect x="0" y="392" width="{W}" height="{H-392}" fill="url(#alu)"/><path d="M0,392 H{W}" stroke="{ENG2}" stroke-width="1.2"/>')
    b.append(text(48, 452, "GABRIEL GHANEM", 44, 700, ls=5))
    b.append(text(50, 488, "MANUFACTURING ENGINEER  ·  CAD / CAM / MACHINING", 15, ls=3))
    return card("\n".join(b))

def b_back():
    cx, cy = W-590, 220
    b = [ripples(cx, cy), spring(cx, cy, flip=-1)]
    b.append(f'<rect x="0" y="392" width="{W}" height="{H-392}" fill="url(#alu)"/><path d="M0,392 H{W}" stroke="{ENG2}" stroke-width="1.2"/>')
    b.append(f'<rect x="520" y="60" width="290" height="290" rx="14" fill="url(#alu)" stroke="{ENG2}" stroke-width="1.2"/>')
    q, n = qr(545, 85, 240); b.append(q)
    b.append(text(48, 440, TAG1, 16, 600, ls=2.4)); b.append(text(48, 464, TAG2, 16, 600, ls=2.4))
    b.append(text(48, 506, PHONE + "   ·   " + MAIL + "   ·   AVAILABLE SEPT. 2027", 12.5))
    b.append(text(W-48, 506, "03 / 12", 13, 700, anchor="end"))
    return card("\n".join(b))

# ---------- C : digital thread — model, toolpath, part ----------
def c_front():
    b = []
    for gx in range(40, 300, 26):  # CAD grid behind stage 1
        b.append(f'<path d="M{gx},110 V400" stroke="{ENG2}" stroke-width=".6" opacity=".55"/>')
    for gy in range(110, 410, 26):
        b.append(f'<path d="M30,{gy} H296" stroke="{ENG2}" stroke-width=".6" opacity=".55"/>')
    ys, sc = 262, .86
    xs = [163, 428, 693]
    b.append(spring(xs[0], ys, "sketch", s=sc)); b.append(spring(xs[1], ys, "toolpath", s=sc)); b.append(spring(xs[2], ys, "part", s=sc))
    for x in (296, 561):
        b.append(f'<path d="M{x-14},{ys} h28 m-9,-7 l9,7 l-9,7" stroke="{ENG}" stroke-width="2" fill="none"/>')
    for x, n_, l in zip(xs, ("01", "02", "03"), ("MODEL", "TOOLPATH", "PART")):
        b.append(text(x, 420, n_, 13, 700, anchor="middle", fill=ENG2))
        b.append(text(x, 442, l, 17, 600, anchor="middle", ls=4))
    b.append(text(48, 66, "GABRIEL GHANEM", 40, 700, ls=5))
    b.append(text(W-48, 52, "MANUFACTURING ENGINEER", 15, anchor="end", ls=3))
    b.append(text(W-48, 74, "FROM CAD TO CHIPS", 15, 700, anchor="end", ls=3))
    b.append(f'<path d="M48,90 H{W-48}" stroke="{ENG}" stroke-width="1.4"/>')
    b.append(f'<path d="M48,478 H{W-48}" stroke="{ENG}" stroke-width="1.4"/>')
    b.append(text(48, 506, "GG-2027-001  ·  REV C  ·  AL 7075-T6", 13))
    b.append(text(W-48, 506, "ONLY ONE OF THESE THREE MOVES.  →", 13, 700, anchor="end"))
    return card("\n".join(b))

def c_back():
    b = []
    cx = W - 693
    b.append(spring(cx, 262, "part", flip=-1, s=.86))
    b.append(text(cx, 420, "03", 13, 700, anchor="middle", fill=ENG2)); b.append(text(cx, 442, "PART", 17, 600, anchor="middle", ls=4))
    q, n = qr(560, 110, 230); b.append(q)
    b.append(text(675, 372, "04", 13, 700, anchor="middle", fill=ENG2)); b.append(text(675, 394, "DIGITAL TWIN", 17, 600, anchor="middle", ls=4))
    b.append(f'<path d="M{cx+150},262 H528 m-9,-7 l9,7 l-9,7" stroke="{ENG}" stroke-width="2" fill="none" stroke-dasharray="none"/>')
    b.append(text(330, 180, TAG1[:20], 15, 600, ls=2)); 
    b.append(text(308, 150, "DESIGNED,", 17, 700, ls=3)); b.pop(-2)
    b.append(text(308, 174, "PROGRAMMED", 17, 700, ls=3)); b.append(text(308, 198, "AND MACHINED", 17, 700, ls=3))
    b.append(text(308, 300, "BY THE PERSON", 13, ls=2.4)); b.append(text(308, 319, "WHO HANDED", 13, ls=2.4)); b.append(text(308, 338, "IT TO YOU.", 13, ls=2.4))
    b.append(f'<path d="M48,478 H{W-48}" stroke="{ENG}" stroke-width="1.4"/>')
    b.append(text(48, 506, PHONE + "   ·   " + MAIL, 13))
    b.append(text(W-48, 506, "AVAILABLE SEPT. 2027   ·   03 / 12", 13, 700, anchor="end"))
    b.append(text(48, 66, "GABRIEL GHANEM", 40, 700, ls=5))
    b.append(f'<path d="M48,90 H{W-48}" stroke="{ENG}" stroke-width="1.4"/>')
    return card("\n".join(b))

if __name__ == "__main__":
    for name, fn in [("A_drawing_front", a_front), ("A_drawing_back", a_back), ("B_ripple_front", b_front),
                     ("B_ripple_back", b_back), ("C_thread_front", c_front), ("C_thread_back", c_back)]:
        (OUT / f"{name}.svg").write_text(fn())
    print("QR modules:", len(list(segno.make(URL, error='m').matrix)))
