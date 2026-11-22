# Handoff: CNC business card (Gabriel Ghanem)

You are taking over a project in progress. Read this whole file, then the repo README, before touching anything.

## 1. What this is and why

Gabriel is a final-year mechanical engineering student (ESILV, work-study) looking for a manufacturing / industrialisation job from September 2027. His hackathon team will pitch a PDM/PLM project to Capgemini, Renault and Dassault Systèmes executives. He wants to hand a few of them a business card he designed, programmed and machined himself, so that it gets shown around afterwards.

The card is a PLM demo in the hand: part number, revision, serial, and a QR code that opens its "digital twin" (CAD, toolpaths, machining video). Rule agreed with Gabriel: **every callout on the card must be a true, checkable statement about the card.** Someone who reads GD&T will spot decoration in seconds.

The online page behind the QR code is not built yet (`docs/index.html` is a placeholder). Gabriel said he will supply photos, videos and CAD for it when we get there.

## 2. Where everything is

| Thing | Location |
|---|---|
| Repo | `github.com/Gabrielgorithme/CNC-Business-card-`, branch `main` (Gabriel has had work pushed straight to `main`) |
| Files on his PC | `C:\Users\gabri\OneDrive\Business Card\` (`cad\` inputs, `cam\` helpers and check G-code) |
| Fusion | Hub "GAB", project "Business card". "Card v3" = current CAM. "Card v2" = first test card, leave it alone |
| Tool library | `hub://GAB/Library.hub` |
| Machine | Genmitsu 3030-PROVer Ultra, FluidNC, 1.5 kW water-cooled spindle, 24,000 rpm, his own `grbl.cps` post in the personal post folder |

Repo layout: `design/v3/` (generator, lettering, mockups, renders), `cad/` (CadQuery model, CAM input export, G-code replay checks), `cam/` (Fusion helper library, Fusion archive, check G-code), `analysis/` (flexure sizing).

## 3. The card as designed (v3)

- ISO ID-1 outline, 85.60 x 53.98, corner radius 3.18, chamfer 0.15 both sides.
- Stock 2.00 mm 7075-T6. Each face is surfaced by 0.15 (0.13, then 0.02 after machining to deburr), so the finished card is **1.70 mm**.
- **Recto:** concentric ripples (wavelength 2.0, amplitude 0.12, a revolved spline about the spring axis, sitting 0.02 below the face), name band, name.
- **Verso:** dense technical face: spring with callouts, hole callout with position tolerance and datums A/B/C, flatness frame, QR code, scallop comparator (three ball-nose patches), S-N curve with the spring's operating point, G-code excerpt, first-angle projection symbol, ruler, rocket outline (his Léofly role), micro-text, contact details.
- **Spring:** orthoplanar, three spiral slots 1 mm wide through a 0.40 mm web centred in the thickness (recess 0.65 from each finished face), boss left full thickness. Sizing in `analysis/flexure_fatigue.py`: 7075 only; about 134 MPa at ±1 mm. Hand calculation, never confirmed by FEA or a cycled coupon.
- **Lettering:** ISOCP as Fusion draws it (`Isocp.shx`). It is a single-line font and Fusion's "Bold" does not change its geometry. Minimum Fusion text height 0.70 mm (0.61 mm capitals), which Gabriel found engraves best. Every text and drawn line is one V pass at fixed depth (width = 2 x depth) in four classes: 0.05, 0.075, 0.10, 0.20 mm. Only closed areas (QR, arrowheads, dots) are V-carved.

The design is generated, not drawn: `design/v3/generate.py` produces the layout, `cad/build_card.py` the 3D model, `cad/export_cam_inputs.py` the CAM inputs (body STEP, trace DXFs by depth layer, fills DXF, helper curves). `design/v3/lettering.py` needs `isocp_fusion_strokes.json`, which is **not in the repo** (glyph data from Autodesk's font). Regenerate it with `cam/dump_isocp_from_fusion.py`, or copy it from `...\Business Card\cad\fonts\` on his PC.

## 4. The process Gabriel settled on

Fixturing is blue tape + CA glue. No tabs: the tape holds parted pieces.

**OP1, verso up.** Face 0.13 (card and ear) → spring recess → holes → part off card + ear (rough then one finishing pass) → deburr recess rim / boss / hole with the 90° tool → single-line engraving → V-carve fills → chamfer → scallop comparator → deburr face 0.02.

**Flip about the long axis onto two 3 mm pins**, glue, pull the pins.

**OP2, recto up.** Face 0.13 → ripples → recess → trim the ear off → deburr → engraving → chamfer → deburr face 0.02 → spiral slots.

Locating the flip uses two Ø3.05 holes: the card's own hole, and one in an **ear** left attached when the card is parted off in OP1 (3.3 mm radius tab centred 2.2 mm outside the short edge, on the long axis; OP2 trims it off). The ear hole is on the flip axis, so its pin hole in the spoilboard is reused. The card hole is off the axis and lands at a mirrored position, so a small third setup ("OP2 prep") drills that one pin hole in the spoilboard.

Tools: T45 4 mm bull-nose (facing, chosen by Gabriel to reduce the tram staircase), T20 2 mm flat, T10 1 mm flat (slots), T43 4 mm 90° engraver, T31 3 mm ball (ripples, comparator). Feeds are in the Fusion operations; T43 runs at 300 mm/min because that is what his trial proved.

Z convention in OP1 and OP2: Z0 on the raw top, finished face at Z-0.15. Each recess is measured from its own raw face, so **the web is the plate thickness minus 1.60**: measure the plate.

## 5. State of the Fusion CAM when I left

Gabriel had been editing "Card v3" himself and had not saved. My last check of his version found three problems; **I do not know whether he fixed them. Check first.**

1. OP2 "Trim the ear off, rough" had its bottom at model bottom with a further -1.85 offset, giving Z-3.70 (1.85 mm into the spoilboard). It should match the finish pass: Z-1.85.
2. OP1 stock was a 100 x 60 fixed box with the card 1 mm from the left edge, origin on the stock corner. The ear sticks out 5.5 mm on that side, so the ear hole (X-1.2) and part-off (to X-6.5) fell outside the plate. X offset needs about 9 mm.
3. OP2 used "previous setup" stock with origin at its top centre, and the prep setup used the card centre. Neither is findable after parting off. I recommended putting both origins on the ear hole.

His deliberate choices, do not undo them: T45 for facing; all T20 work straight after facing; holes and part-off stop exactly at the underside (Z-2.00 in OP1, Z-1.85 in OP2) because cutting deeper fills the end mill with tape glue; his board already has its pin holes; one suppressed operation named "OLD 3 Holes…" and an unused circle in `CAM REF_HOLES` are leftovers.

`cam/Card_v3.f3d` and `cam/gcode_check_v3/` in the repo predate his edits.

## 6. Your tasks

### A. Catch up
Read the README, open "Card v3", list setups, operations, tools, heights and origins, and compare with section 4 and 5. Ask Gabriel what his tests showed before changing the design.

### B. Update the design after his testing
- **Hole callout.** The verso still says "Ø3 H7 (+0.010/0)" with position Ø0.05 to A, B, C, and the model has a Ø3 hole. The CAM mills Ø3.05 with a 2 mm end mill. Make the model, the callout and its tolerance match what he measures. Keep the position tolerance only if his flip registration really holds it.
- **QR code.** It encodes a long placeholder GitHub Pages URL (33 x 33 modules, 0.67 mm each). Its finder squares V-carve 1.05 mm deep, leaving 0.51 mm of metal. If his test scans poorly or cuts too deep: get a short final URL (a redirect he controls) to drop to fewer, larger modules, and consider one V plunge per module. Contrast on bare aluminium was the known risk.
- **Engraving depths.** I chose the four classes; he never told me the depth his good 0.7 mm trial used. Ask.
- **Serial number.** The card says "03 / 12". A batch needs a different serial on every card and the right total.
- **Other claims to make true:** S-N curve (approximate handbook values, needs a source), mass "≈ 19.5 g" (computed, not weighed), the G-code excerpt (invented lines, replace with real ones), "R1.5 BALL" and the scallop heights, "Ra 0.8", "NO LASER WAS USED", part number and revision, the flatness and profile tolerances.
- Regenerate `design/v3/`, the model and the CAM inputs from the scripts, and push.

### C. Batch CAM on 300 x 200 mm plates
- Copy his tested CAM exactly (operations, order, tools, feeds, heights), applied to the updated design.
- **OP1:** as many cards as fit in the plate, each with its own ear and both holes. **OP2:** one card at a time on the pin fixture, so a single OP2 program.
- Rough count, to verify with real margins: card + ear + 2 mm slot gives a pitch of about 95 x 58 mm, so around 9 with the long side along 300 and possibly 10 turned the other way. Leave room for the facing overrun, a web between slots, and whatever he needs at the plate edge. Ears can face each other to save space.
- Decide with him: one facing pass over the whole plate or per card (flatness over 300 mm on a hobby machine matters for 0.05 mm engraving), and the operation order across cards (by tool across the plate to save tool changes, versus finishing a card before parting it).
- Each card has a different serial, so the engraving geometry differs per position.

## 7. Working with Fusion through the MCP: lessons that cost time

- Scripts run with `featureType: "script"`; define `run(_context)`. `cam/fusion_lib.py` (also in his OneDrive `cam\` folder, importable with `sys.path.insert`) has helpers for tools, selections, generation and posting.
- **A failed script does not roll back cleanly.** CAM changes made before the exception stay; sketches created in the same script disappear. Create sketches in their own script, and wrap CAM work in try/except that prints.
- After opening or saving a document, call `doc.activate()` before switching workspace, or the CAM product is missing and `activeWorkspace` throws.
- DXF and STEP import only work in the Design workspace (`FusionSolidEnvironment`); CAM is `CAMEnvironment`.
- `setup.workCoordinateSystem` lags one change behind; pump events and re-read. Setting "top center" after flipping Z needs the box point set to something else and back.
- **Chain direction decides the side** for 2D pocket and contour, and it flips with the setup: in the verso setup pocket chains needed `isReverted = True`; in the recto setup contours needed it. My first pocket cleared the whole stock around the card. Never trust a selection without checking the result.
- 2D chamfer on model edges gave an empty toolpath; a sketch contour with explicit width and heights works.
- The trace strategy follows the sketch Z plus `axialOffset`; all sketches sit at model Z = 0, so recto traces use `1.70 - depth`.
- If Fusion stops answering (80 s timeouts), it is busy or showing a dialog. Ask Gabriel; do not blindly retry anything that writes.
- Gabriel edits the document live. Read its state before every change, never overwrite his settings, and say before saving.

## 8. How the CAM is verified

Post every operation separately with his `grbl.cps` into `cam\check_v3\`, write the setups' coordinate systems to `meta.json`, stage the files, and run `cad/verify_nc_v3.py`. It replays lines and arcs and checks each operation against the design geometry: engraving stays on the drawn lines at the right depth, V-carve never leaves the fills, pocket radii, hole diameters, tool edge versus outline, cut-through coverage, facing coverage, no XY rapids near the surface. It caught every real error so far. It is **not** a collision or holder simulation, and nothing replaces Gabriel simulating in Fusion.

Extend the script when operations change; do not delete a check to make it pass.

## 9. How Gabriel works

- Direct and technical. He pushes back when reasoning is wrong and dislikes hedging or being talked down to.
- He wants accurate UI instructions for the exact software, or none.
- He does the machining and makes the process decisions; you do design, CAD and CAM, and you tell him plainly when something he set will not work, with numbers.
- Tell him what you assumed. Several of my defaults (reference holes, part-off in OP2) were replaced by his better shop-floor choices once he saw them.
- Personal email for the card: Gabriel.ghanem@gmail.com. Phone as engraved: +33 6 60 45 50 18.

## 10. Known risks still open

- Plate thickness sets the web (2.05 mm plate → 0.45 mm web).
- Cutting exactly to the underside leaves a foil if the plate is over nominal.
- The unsupported 0.40 mm web can deflect when the second recess is cut.
- Pin-to-hole play (3.05 on 3 mm pins) shows as a small step where OP2 trims the ear.
- T43 is defined with a perfect point; a real tip flat widens every thin line.
- Bright-on-black anodising was discussed as the way to make engraving stand out; it means re-fixturing after the bath. Not decided.
