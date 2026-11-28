"""Build the portfolio's static pages into docs/: index.html (English), fr/index.html (French), 404.html.

    python3 site/build.py

Headings are drawn at build time with the card's ISOCP strokes (site/isocp.py), so the published pages are plain
HTML with inline SVG: no framework, no runtime dependency for the lettering."""
import hashlib, html, json, pathlib, re
import isocp

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
URL = "https://gabrielgorithme.github.io/CNC-Business-card-/"
SIZES = json.loads((DOCS / "assets/img/sizes.json").read_text())


def ver(rel):
    """Content fingerprint for cache busting: browsers keep CSS and JS for a while, so a change must change the URL."""
    return hashlib.sha1((DOCS / rel).read_bytes()).hexdigest()[:8]
EMAIL = "gabriel.ghanem@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/gabriel-ghanem-02528a208"
GGSENDER = "https://github.com/Gabrielgorithme/GGSender"


def L(text, weight=None, track=0.0, cls="", label=None, lead=1.5):
    """ISOCP lettering with its text kept for screen readers and search."""
    lab = html.escape(label if label is not None else text.replace("|", " "))
    return f'<span class="sr">{lab}</span>' + isocp.svg(text, weight=weight, track=track, cls=cls, lead=lead)


def img(name, alt, sizes="100vw", cls="", eager=False, prefix=""):
    m = SIZES[name]; ws = m["widths"]
    srcset = ", ".join(f"{prefix}assets/img/{name}-{w}.webp {w}w" for w in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{prefix}assets/img/{name}-{ws[-1]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{m["w"]}" height="{m["h"]}" alt="{html.escape(alt)}" {load}>')


def fig(name, alt, cap=None, sizes="100vw", prefix="", cls=""):
    c = f"<figcaption>{cap}</figcaption>" if cap else ""
    k = f' class="{cls}"' if cls else ""
    return f"<figure{k}>{img(name, alt, sizes, prefix=prefix)}{c}</figure>"


def row_sizes(name, row=300):
    """Strip photos are laid out by height, so their rendered width follows their aspect ratio."""
    m = SIZES[name]
    return f"{round(row * m['w'] / m['h'])}px"


def fold(body):
    """Each <h3> and the text up to the next one becomes a closed <details>; text before the first <h3> stays visible."""
    parts = re.split(r"<h3>(.*?)</h3>", body)
    out = parts[0]
    for title, text in zip(parts[1::2], parts[2::2]):
        out += f'<details><summary><h3>{title}</h3></summary><div class="fold">{text.strip()}</div></details>\n'
    return out


def fr_typo(s):
    """French spacing: narrow no-break space before ; : ! ? and inside guillemets (text only, not tags or URLs)."""
    parts = re.split(r"(<[^>]+>)", s)
    for i, p in enumerate(parts):
        if p.startswith("<"): continue
        p = re.sub(r" ([;:!?»])", " \\1", p)
        p = re.sub(r"« ", "« ", p)
        parts[i] = p
    return "".join(parts)


# ---------------------------------------------------------------- copy
T = {
"en": dict(
    lang="en", other="fr/", other_label="Français", other_lang="fr", prefix="",
    title="Gabriel Ghanem, mechanical engineer: design and machining",
    desc="Final-year mechanical engineering student at ESILV, working across design and production: a CubeSat accelerometer, the tank of a REXUS experiment, a reverse-draw crossbow. Looking for a permanent job in manufacturing or methods engineering from September 2027.",
    part="Part GG-2027-001, revision C",
    me_alt="Gabriel on a rooftop at sunset, between two of Léofly's rockets.",
    lead="Mechanical engineering student, final year at ESILV. I work on problems that span design and production, at both scales: the overall architecture of a system, and the tolerance, surface finish or fixture that decides whether it can be made.",
    avail="<strong>Looking for a permanent job (CDI) from September 2027</strong> in manufacturing, industrialisation or methods engineering, in the Paris area.",
    email="Email", cv="CV (PDF)", cvfile="assets/cv/gabriel-ghanem-cv-en.pdf",
    jump='<a href="#card">The program that engraved your card</a>',

    cs_h="MAGNETIC|ACCELEROMETER", cs_label="Magnetic accelerometer",
    cs_ctx="A 1U CubeSat experiment for Léofly, my rocketry club. 2023 to 2026.",
    cs_alt="Section render of the accelerometer: a magnet on a flat spring inside a clear oil tank, PCBs below, aluminium frame.",
    cs_call=("MAGNET", "SPRING|POM-C 0.7", "PMMA|OIL TANK"),
    cs_sum="A magnet on a flat spring, damped in oil, read by two Hall sensors at 8 kHz. I designed the mechanics and the model that turns the two signals into an acceleration, then machined the parts.",
    tb=(("Format", "1U", "100 × 100 × 100 mm"), ("Range", "±17", "g; the rocket peaks at 15 g"),
        ("RMS error", "2", "%, and 5 % at worst"), ("Sampling", "8", "kHz, 2 Hall sensors")),
    tb_label="Key figures",
    spring_alt="White POM-C ortho-planar spring lying on an aluminium block that carries its test-cut outline.",
    spring_spec="Spring specification: parallelism 0.02 mm to datum A, inspected held flat (ISO 10579-NR), roughness Ra 0.8 µm.",
    spring_cap="The POM-C spring on the block where I test-cut its outline. The 0.02 mm is a parallelism checked with the spring held flat: a 0.7 mm plastic disc warps as soon as you let go of it, so checking it free would reject good parts.",
    cs_body="""
<h3>Where it started</h3>
<p>In 2023 the club wanted to build a laser accelerometer. I read up on how they work and said it would be too complicated for us, but that we could probably make one with a magnet, a spring and a Hall sensor. I knew Hall sensors because I'd just repaired the throttle on my electric scooter.</p>
<h3>How it works</h3>
<p>A magnet sits on an ortho-planar spring: a flat disc cut with spiral slots, so its centre moves straight up and down without turning. When the rocket accelerates, the magnet moves. Two Hall sensors, one on each side, read the change in field, and a model turns the two signals into an acceleration. The spring sits in an oil bath so the magnet settles quickly instead of ringing after every shock.</p>
<h3>From a strip of PLA to an ortho-planar spring</h3>
<p>My first spring was just a thin strip of printed PLA bending under the magnet. Another student told me to look up ortho-planar springs, so I printed one. The final spring is machined from POM-C.</p>
<h3>Reading the spring backwards</h3>
<p>If the spring sits still at a given displacement, working out the acceleration is easy. Mine bounced around, so every reading depended on the magnet's inertia and on everything that had just happened before. At the same time I was taking a control-systems class, and I couldn't connect Laplace transforms to anything I could actually build. Then it clicked: this was a control loop backwards. A PID drives an input to get the output you want; I only had the wobbly output and needed to work back to the input that caused it. Needless to say, I passed the class.</p>
<h3>What went wrong</h3>
<p>In practice it wasn't clean. Just holding the prototype in my hand made it vibrate and resonate, and the signal was too messy to work back from. The more the old bounces leak into the reading, the worse it gets, so they had to die out faster: I needed to damp the mass. The spring was sensitive enough that I could afford to lose some of that. After a couple of damping attempts that didn't work, I bought a Tupperware and a bottle of vegetable oil and dropped the spring in. People thought I was crazy, until the signal, cleaned up in MATLAB and Simulink, started looking like a commercial sensor's.</p>
<p>The oil then caused a new problem: it crept up the Arduino's wires by capillary action. In the final build the loose wires became custom PCBs, the printed chassis became milled aluminium, and the Tupperware became a machined PMMA tank.</p>
<h3>Calibration</h3>
<p>The coefficients I calculated from measuring the parts gave me nothing usable. So I fitted the model to real recordings instead, which worked. Shaken next to a commercial accelerometer, it now follows it within 2 % RMS, 5 % at worst, over ±17 g. The rocket peaks at about 15 g.</p>
<h3>Decisions</h3>
<p><b>The spring material.</b> The final spring is machined from POM-C, 0.7 mm thick, made with PBMC, one of the club's partners. POM-C creeps less under constant load, takes repeated bending better and isn't attacked by oil, while polycarbonate tends to crack under stress in contact with many oils. A machined part is also uniform; a printed one has layer lines that act like notches.</p>
<p><b>Tolerances from simulation.</b> I ran a parametric Ansys study of manufacturing defects to see how far they move the spring's response, and set two specs from it: 0.02 mm parallelism between the faces, measured with the spring held flat, and Ra 0.8 µm.</p>
<p><b>The housing.</b> Machined aluminium throughout. The oil tank is machined from PMMA so the spring stays visible, and the seals are printed in TPU 60A.</p>
<h3>My part</h3>
<p>I designed the mechanics and the mathematical model, laid out one of the three PCBs in KiCad, wrote the signal processing, ran the FEA and machined the parts. Julien Finkler designed the other two PCBs.</p>""",
    cs_proto=("cubesat-proto", "First prototype: Arduino, 3D-printed chassis and a glued acrylic tank on a red table.", "Prototype 1: Arduino, printed chassis, glued tank."),
    cs_final=("cubesat-final", "Final build: machined aluminium frame and clear PMMA tank.", "Final: milled frame and PMMA tank."),
    cs_more=(("cubesat-pcbs", "Three custom PCBs and a machined aluminium plate.", "The PCBs and a machined plate."),
             ("cubesat-tank", "The machined PMMA oil tank on its own.", "The PMMA tank, machined."),
             ("cubesat-talk", "Gabriel presenting the accelerometer beside a rocket and a slide.", "Presenting it at a partner's event.")),

    lf_h="LÉOFLY", lf_label="Léofly",
    lf_ctx="ESILV's experimental rocketry club, since 2023. Rockets and payloads for the C'Space (CNES) and EuRoC campaigns.",
    lf_group=("Gabriel teaching a group of club members in front of the school's CNC machining centre.", "Machine-tool training for the members, in front of the school's machining centre, October 2025."),
    lf_more=(("leofly-teach-lathe", "Gabriel explaining the tool turret of the school's CNC lathe.", "Training on the CNC lathe."),
             ("leofly-stand", "The club's stand at an event: five rockets in front of a banner of partners.", "The club's stand, with our rockets."),
             ("stard-tank", "Two machined aluminium tank halves with printed TPU gaskets and O-rings on a printer bed.", "STAR-D: the tank halves for the phase-change fluid, with their printed TPU gaskets."),
             ("stard-module", "The STAR-D module, a blue cylinder, with the connector box being fitted.", "STAR-D: the connector box going into the module.")),
    lf_body="""
<p class="keep">I joined in 2023 and worked on the Xénon rocket (CAD, CAM, FEA). From 2024 to 2026 I was technical director, in charge of manufacturing, and since 2026 I've been the club's design and manufacturing referent.</p>
<ul>
<li>Led the teams on the Krypton rocket.</li>
<li>Ran the CAD, CAM and machine-tool training for the members, on the school's CNC machines.</li>
<li>Machined aluminium structure rings, steel and PMMA parts, and laid up carbon structures.</li>
<li>Designed the CubeSat accelerometer above.</li>
</ul>
<h3>STAR-D, an experiment on REXUS 38</h3>
<p>STAR-D (Space Test of Amoeba Response: Dictyostelium) uses the amoeba <i>Dictyostelium discoideum</i> to study how reduced gravity affects the early stages of the immune response, and whether this organism could stand in for human immune cells in future space experiments. It runs as a fully autonomous lab on the REXUS 38 sounding rocket, from launch to recovery, with a launch planned for March 2027. The team comes from ESILV, AgroParisTech, Newcastle University and the University of Vienna.</p>
<p>I wasn't on the team. They brought me in for the machining and to make their parts easier to manufacture:</p>
<ul>
<li>Machined the aluminium tank for the phase-change fluid, and printed its gaskets in TPU 60A, since nothing off the shelf had the right shape.</li>
<li>Helped define the sealing tolerances and surface specifications.</li>
<li>Reworked parts of the CAD to cut the cost of the parts outsourced to JLCCNC.</li>
<li>Drew a large share of the connector box CAD and drawings.</li>
<li>Adjusted the rails and other parts for an exact fit.</li>
</ul>""",

    xb_h="REVERSE-DRAW|CROSSBOW", xb_label="Reverse-draw crossbow",
    xb_ctx="Personal project, designed and built from scratch. Still a prototype.",
    xb_cad="CAD", xb_proto="PROTOTYPE",
    xb_range="Compare the CAD model with the first full prototype",
    xb_alt_cad="SolidWorks model of the crossbow, parts in different colours.",
    xb_alt_proto="First full prototype of the crossbow standing upright in a vice.",
    xb_body="""
<p class="keep">32 CNC-machined aluminium parts, third iteration after a PETG prototype and a laminated carbon one.</p>
<h3>Why reverse draw</h3>
<p>In a reverse-draw crossbow the limbs point back towards the shooter, so the string travels further for the same width and the weight sits closer to the grip. It also makes the cams and the cocking mechanism harder to design, which is the part I wanted to work on.</p>
<h3>Decisions</h3>
<p><b>One model drives everything.</b> The SolidWorks assembly is driven by a shared equations file, so changing one dimension updates every part that depends on it.</p>
<p><b>Check before cutting aluminium.</b> Each new geometry was tested in POM-C or 3D printed before I machined it. The limbs are glass fibre; I prototyped them in POM.</p>
<p><b>A simulator for the cocking mechanism.</b> I built it with help from AI: I can change the shape and position of the parts live and the kinematics update instantly, so I can try ideas without going back into CAD.</p>
<p><b>Machining.</b> 32 parts in 6061, 7075 and 5052 aluminium, held by 120 fasteners. Adaptive toolpaths, multi-operation fixtures, minimum-quantity lubrication.</p>""",
    xb_more=(("crossbow-cam", "A machined aluminium cam with its bearing, held in the hand.", "A cam, straight off the machine."),
             ("crossbow-top", "The prototype seen from above on the bench.", "From above: the limbs point back."),
             ("crossbow-lever", "The green printed cocking lever in use.", "The cocking lever.")),

    hk_h="GRAPPLING HOOK", hk_label="Grappling hook",
    hk_ctx='Personal project. 6061 aluminium and a brass tip. <a href="https://www.esilv.fr/un-grappin-articule-un-projet-dinnovation-technique-concu-a-lesilv/" hreflang="fr">Featured in an article on ESILV\'s website</a> (in French).',
    hk_body="""
<p class="keep">Turned and milled, with arms that fold along the shaft. The idea came from friends who wanted one for climbing.</p>
<h3>Manual first, then CNC</h3>
<p>I made the first version on manual machines. When I wanted more complex shapes, the workshop teacher told me to stop spending hours doing by hand what a CNC does better. So I redrew it for CNC and wrote the CAM myself: serrated arms, a knurled grip, and a brass tip, for the looks and for the weight at the bottom.</p>
<p>CNC and manual lathe and mill. The arms come out of plate stock with adaptive toolpaths; the shaft is turned between centres.</p>""",
    hk_imgs=(("hook-deployed", "The aluminium grappling hook held up with its three arms open.", "Arms open."),
             ("hook-folded", "The hook with its arms folded along the shaft.", "Arms folded.")),
    hk_more=(("hook-cnc-manual", "The CNC version in front of the earlier manual version.", "CNC version in front, manual version behind."),
             ("hook-lathe", "The shaft being turned on a CNC lathe, supported by the tailstock.", "Turning the shaft."),
             ("hook-arm", "An arm half-machined in its aluminium plate.", "An arm, half-machined in its plate."),
             ("hook-fea", "Ansys static structural study of one arm, coloured by safety factor.", "Static study of an arm in Ansys.")),

    mg_h="CARBON MUDGUARD", mg_label="Carbon mudguard",
    mg_body="For my 1,500 W electric bike: I scanned the bike with a phone app, designed the mudguard on the scan, printed the mould in four sections and laid up the carbon by hand.",
    mg_imgs=(("mudguard-scan", "The mudguard designed on a 3D scan of the bike, in four coloured mould sections."),
             ("mudguard-layup", "Carbon layup on the printed mould."),
             ("mudguard-fitted", "The finished carbon mudguard on the bike's rear wheel.")),

    cn_h="CNC RETROFIT AND GGSENDER", cn_label="CNC retrofit and GGSender",
    cn_body=f'I rebuilt my CNC router around a FluidNC controller and a water-cooled 1.5 kW spindle driven over Modbus RS485. Then I forked the open-source gSender software into <a href="{GGSENDER}">GGSender</a>, with AI assistance, to rework the tool-change sequence so tools keep their full usable length, and to keep a persistent log of the controller traffic for diagnosis. Most parts on this page were cut on it.',
    cn_img=("cnc-machine", "The CNC router in its sound-proofed enclosure, crossbow parts on the bench and the sender software on a screen."),

    cd_h="THE CARD YOU SCANNED", cd_label="The card you scanned",
    cd_ctx="Milled from aluminium plate on that same machine, raw finish. The disc in the middle is an ortho-planar spring, the same kind as in the accelerometer.",
    cd_body="This is the engraving program I wrote for the back of your card, replayed: <b>25,354 lines of G-code</b>, one 90° V-bit.",
    cd_replay="Replay",

    xp_h="EXPERIENCE",
    xp=[
        ("Ambiance Lumière, Alfortville", "JULY 2025 - SEPT. 2027", "Industrial design engineer, work-study",
         ["A maker of custom architectural lighting, from prototype to small series.",
          "54 high-end luminaire projects, 19 of them carried alone from the client's brief to the manufacturing drawings. Among them, a façade luminaire made 300 times with suppliers in France and Asia, and a luminaire for a luxury fashion house's 2025 Christmas campaign.",
          "Commissioned the company's CNC mill and machined its first parts.",
          "Luminaires for Notre-Dame de Paris during its restoration.",
          "I design custom tooling and measuring equipment for the workshop. One rig sets the distance between a lens and its LED with a twist of its top part, and reads it off engraved graduations.",
          "Thermal simulation, optical measurements, supplier follow-up."],
         (("ambiance-notredame", "Oak spiral staircase under the medieval timber frame of a Notre-Dame tower, lit by linear luminaires in the handrail and along the beams.", "Notre-Dame de Paris, restored: lighting in the towers."),
          ("ambiance-belfry", "A bronze bell in its timber belfry at Notre-Dame, lit from below the beams.", "Notre-Dame de Paris: the belfry."),
          ("ambiance-showcase", "Shop-window display for a luxury fashion house: a topiary butterfly studded with points of light, a bag at its centre.", "A window display for a luxury fashion house."),
          ("ambiance-rig", "Printed rig holding a flexible LED strip under magenta light.", "A measuring rig: lens-to-LED distance."),
          ("ambiance-4axis", "A block being machined on a 4-axis mill with a rotary axis.", "4-axis machining."),
          ("ambiance-cfd", "Convection streamlines around two heatsink designs: straight fins and concentric rings.", "Convection study of two heatsink designs."))),
        ("Pôle Léonard de Vinci", "2023 - 2024", "Workshop and lab assistant, part-time",
         ["Maintained the workshop's machine tools, installed safety devices, wrote technical documentation."], ()),
    ],

    ed_h="EDUCATION AND TOOLS",
    ed="""
<p><b>ESILV, Paris-La Défense</b>: engineering degree (diplôme d'ingénieur, master's level), major in modelling and computational mechanics. 2022 to 2027, work-study since 2025. In 2027, nine weeks of hands-on welding training in Dublin.</p>
<p>I model in SolidWorks and Fusion 360, and have also worked in CATIA, 3DEXPERIENCE and Onshape. I program CAM in Fusion 360, 3DEXPERIENCE and Vectric Aspire. I run FEA in Ansys and Abaqus, plus thermal simulation, lay out PCBs in KiCad, and write Python, MATLAB, C++ and C#.</p>
<p>In the workshop: 3- and 4-axis CNC milling, CNC and manual turning and milling, fixtures, carbon composites, resin casting, FDM and SLA printing, and machine maintenance.</p>
<p>French (native), English C1 (TOEFL ITP 663/677), German (basics).</p>""",

    ct_h="CONTACT",
    ct="I'm looking for a permanent job (CDI) in manufacturing, industrialisation or methods engineering from September 2027, in the Paris area.",
    colophon="The headings use the actual strokes engraved on the card, pulled out of its design files. Body text is Atkinson Hyperlegible Next.",
    nf_title="Page not found", nf="This page doesn't exist. The card's QR code leads to the home page.", nf_link="Go to the home page",
),
}

T["fr"] = dict(T["en"])
T["fr"].update(
    lang="fr", other="../", other_label="English", other_lang="en", prefix="../",
    title="Gabriel Ghanem, ingénieur mécanique : conception et usinage",
    desc="Élève ingénieur mécanique en dernière année à l'ESILV, entre conception et production : un accéléromètre pour CubeSat, le réservoir d'une expérience REXUS, une arbalète à armement inversé. Je cherche un CDI en fabrication ou en méthodes à partir de septembre 2027.",
    part="Pièce GG-2027-001, révision C",
    me_alt="Gabriel sur un toit au coucher du soleil, entre deux fusées de Léofly.",
    lead="Élève ingénieur mécanique, en dernière année à l'ESILV. Je travaille sur des problèmes qui traversent la conception et la production, aux deux échelles : l'architecture d'ensemble d'un système, et la tolérance, l'état de surface ou le montage qui décident s'il peut être fabriqué.",
    avail="<strong>Je cherche un CDI à partir de septembre 2027</strong> d'ingénieur fabrication, industrialisation ou méthodes, en Île-de-France.",
    email="E-mail", cv="CV (PDF)", cvfile="assets/cv/gabriel-ghanem-cv-fr.pdf",
    jump='<a href="#card">Le programme qui a gravé votre carte</a>',

    cs_h="ACCÉLÉROMÈTRE|MAGNÉTIQUE", cs_label="Accéléromètre magnétique",
    cs_ctx="Une expérience CubeSat 1U pour Léofly, mon association de fusées. De 2023 à 2026.",
    cs_alt="Rendu en coupe de l'accéléromètre : un aimant sur un ressort plat dans un réservoir d'huile transparent, les PCB en dessous, un châssis en aluminium.",
    cs_call=("AIMANT", "RESSORT|POM-C 0,7", "RÉSERVOIR|PMMA"),
    cs_sum="Un aimant sur un ressort plat, amorti dans l'huile, lu par deux capteurs à effet Hall à 8 kHz. J'ai conçu la mécanique et le modèle qui transforme les deux signaux en accélération, puis j'ai usiné les pièces.",
    tb=(("Format", "1U", "100 × 100 × 100 mm"), ("Étendue", "±17", "g ; la fusée culmine à 15 g"),
        ("Erreur RMS", "2", "%, et 5 % au pire"), ("Échantillonnage", "8", "kHz, 2 capteurs Hall")),
    tb_label="Chiffres clés",
    spring_alt="Ressort ortho-planaire blanc en POM-C posé sur un bloc d'aluminium qui porte l'essai d'usinage de son contour.",
    spring_spec="Spécification du ressort : parallélisme 0,02 mm par rapport à la référence A, contrôlé maintenu à plat (ISO 10579-NR), rugosité Ra 0,8 µm.",
    spring_cap="Le ressort en POM-C sur le bloc où j'ai fait un essai d'usinage de son contour. Les 0,02 mm sont un parallélisme contrôlé ressort maintenu à plat : un disque plastique de 0,7 mm se voile dès qu'on le lâche, donc le contrôler libre ferait rejeter des pièces bonnes.",
    cs_body="""
<h3>Le point de départ</h3>
<p>En 2023, l'association voulait faire un accéléromètre laser. Je me suis renseigné sur leur fonctionnement et j'ai dit que ce serait beaucoup trop compliqué pour nous, mais qu'on pouvait sûrement en faire un avec un aimant, un ressort et un capteur à effet Hall. Je connaissais ces capteurs parce que je venais de réparer l'accélérateur de ma trottinette électrique.</p>
<h3>Le principe</h3>
<p>Un aimant est monté sur un ressort ortho-planaire : un disque plat découpé de fentes en spirale, dont le centre monte et descend sans tourner. Quand la fusée accélère, l'aimant se déplace. Deux capteurs à effet Hall, un de chaque côté, lisent la variation du champ, et un modèle transforme les deux signaux en accélération. Le ressort baigne dans l'huile, pour que l'aimant se stabilise vite au lieu de vibrer après chaque choc.</p>
<h3>D'une lamelle de PLA au ressort ortho-planaire</h3>
<p>Mon premier ressort, c'était juste une fine lamelle de PLA imprimée qui pliait sous l'aimant. Un autre étudiant m'a conseillé de regarder les ressorts ortho-planaires, alors j'en ai imprimé un. Le ressort final est usiné en POM-C.</p>
<h3>Lire le ressort à l'envers</h3>
<p>Si le ressort reste immobile à un déplacement donné, l'accélération se calcule facilement. Le mien rebondissait : chaque mesure dépendait de l'inertie de l'aimant et de tout ce qui venait de se passer. En même temps, je suivais le cours d'automatismes et asservissements, et je ne voyais pas le lien entre les transformées de Laplace et quoi que ce soit de concret. Puis le déclic : c'était un asservissement à l'envers. Un PID pilote une entrée pour obtenir la sortie voulue ; moi, je n'avais que la sortie qui oscille et je devais remonter à l'entrée qui l'avait causée. Inutile de dire que j'ai validé le cours.</p>
<h3>Ce qui n'a pas marché</h3>
<p>En pratique, ce n'était pas propre. Rien qu'en tenant le prototype dans la main, il vibrait et entrait en résonance, et le signal était trop chaotique pour remonter à l'accélération. Plus les anciens rebonds se mélangent à la mesure, pire c'est, donc il fallait qu'ils s'éteignent plus vite : amortir la masse. Le ressort était assez sensible pour que je puisse en perdre un peu. Après quelques essais d'amortissement ratés, j'ai acheté un Tupperware et une bouteille d'huile végétale, et j'ai plongé le ressort dedans. On m'a pris pour un fou, jusqu'à ce que le signal, nettoyé sous MATLAB et Simulink, ressemble à celui d'un capteur du commerce.</p>
<p>Ensuite, l'huile a posé un nouveau problème : elle remontait le long des fils de l'Arduino par capillarité. Dans la version finale, les fils volants sont devenus des PCB sur mesure, le châssis imprimé un châssis en aluminium fraisé, et le Tupperware un réservoir en PMMA usiné.</p>
<h3>L'étalonnage</h3>
<p>Les coefficients que j'avais calculés à partir des mesures des pièces ne donnaient rien d'exploitable. J'ai donc calé le modèle directement sur des enregistrements réels, et ça a fonctionné. Secoué à côté d'un accéléromètre du commerce, il le suit à 2 % RMS près, 5 % au pire, sur ±17 g. La fusée monte à environ 15 g.</p>
<h3>Les choix</h3>
<p><b>Le matériau du ressort.</b> Le ressort final est usiné en POM-C, épaisseur 0,7 mm, réalisé avec PBMC, l'un des partenaires de l'association. Le POM-C flue moins sous charge constante, résiste mieux aux flexions répétées et ne craint pas l'huile, alors que le polycarbonate a tendance à fissurer sous contrainte au contact de nombreuses huiles. Une pièce usinée est aussi homogène, alors qu'une pièce imprimée a des couches qui jouent le rôle d'entailles.</p>
<p><b>Des tolérances issues de la simulation.</b> J'ai mené une étude Ansys paramétrique des défauts de fabrication pour voir de combien ils décalent la réponse du ressort, et j'en ai tiré deux spécifications : un parallélisme de 0,02 mm entre les faces, mesuré ressort maintenu à plat, et un Ra de 0,8 µm.</p>
<p><b>Le boîtier.</b> Entièrement en aluminium usiné. Le réservoir d'huile est usiné dans du PMMA pour garder le ressort visible, et les joints sont imprimés en TPU 60A.</p>
<h3>Mon rôle</h3>
<p>J'ai conçu la mécanique et le modèle mathématique, routé l'un des trois PCB sous KiCad, écrit le traitement du signal, fait les calculs par éléments finis et usiné les pièces. Julien Finkler a conçu les deux autres PCB.</p>""",
    cs_proto=("cubesat-proto", "Premier prototype : Arduino, châssis imprimé en 3D et réservoir acrylique collé, sur une table rouge.", "Prototype 1 : Arduino, châssis imprimé, réservoir collé."),
    cs_final=("cubesat-final", "Version finale : châssis en aluminium usiné et réservoir en PMMA transparent.", "Version finale : châssis et réservoir fraisés."),
    cs_more=(("cubesat-pcbs", "Les trois PCB sur mesure et une plaque d'aluminium usinée.", "Les PCB et une plaque usinée."),
             ("cubesat-tank", "Le réservoir d'huile en PMMA usiné, seul.", "Le réservoir en PMMA, usiné."),
             ("cubesat-talk", "Gabriel présente l'accéléromètre à côté d'une fusée et d'une diapositive.", "Présentation lors d'un événement partenaire.")),

    lf_h="LÉOFLY", lf_label="Léofly",
    lf_ctx="L'association de fusées expérimentales de l'ESILV, depuis 2023. Fusées et charges utiles pour les campagnes C'Space (CNES) et EuRoC.",
    lf_group=("Gabriel forme un groupe de membres de l'association devant le centre d'usinage CNC de l'école.", "Formation machines-outils des membres, devant le centre d'usinage de l'école, octobre 2025."),
    lf_more=(("leofly-teach-lathe", "Gabriel explique la tourelle porte-outils du tour CNC de l'école.", "Formation sur le tour CNC."),
             ("leofly-stand", "Le stand de l'association lors d'un événement : cinq fusées devant une bâche de partenaires.", "Le stand de l'association, avec nos fusées."),
             ("stard-tank", "Deux demi-réservoirs en aluminium usinés, avec joints TPU imprimés et joints toriques, sur un plateau d'imprimante.", "STAR-D : les demi-réservoirs du fluide à changement de phase et leurs joints TPU imprimés."),
             ("stard-module", "Le module STAR-D, un cylindre bleu, pendant le montage du boîtier de connecteurs.", "STAR-D : le boîtier de connecteurs entre dans le module.")),
    lf_body="""
<p class="keep">J'ai rejoint l'association en 2023 et travaillé sur la fusée Xénon (CAO, FAO, calcul par éléments finis). De 2024 à 2026, j'ai été directeur technique, responsable fabrication, et depuis 2026 je suis référent conception et fabrication.</p>
<ul>
<li>J'ai encadré les équipes de la fusée Krypton.</li>
<li>J'ai animé les formations CAO, FAO et machines-outils des membres, sur les machines CNC de l'école.</li>
<li>J'ai usiné des bagues de structure en aluminium, des pièces en acier et en PMMA, et stratifié des structures en carbone.</li>
<li>J'ai conçu l'accéléromètre CubeSat présenté plus haut.</li>
</ul>
<h3>STAR-D, une expérience sur REXUS 38</h3>
<p>STAR-D (Space Test of Amoeba Response: Dictyostelium) utilise l'amibe <i>Dictyostelium discoideum</i> pour étudier l'effet de la gravité réduite sur les premières étapes de la réponse immunitaire, et pour savoir si cet organisme pourrait remplacer les cellules immunitaires humaines dans de futures expériences spatiales. C'est un laboratoire entièrement autonome à bord de la fusée-sonde REXUS 38, du lancement à la récupération, avec un lancement prévu en mars 2027. L'équipe réunit l'ESILV, AgroParisTech, l'université de Newcastle et l'université de Vienne.</p>
<p>Je ne faisais pas partie de l'équipe. Ils sont venus me chercher pour l'usinage et pour rendre leurs pièces plus faciles à fabriquer :</p>
<ul>
<li>Usiné le réservoir en aluminium du fluide à changement de phase, et imprimé ses joints en TPU 60A, faute de joint du commerce à la bonne forme.</li>
<li>Participé à la définition des tolérances d'étanchéité et des états de surface.</li>
<li>Repris une partie de la CAO pour réduire le coût des pièces sous-traitées chez JLCCNC.</li>
<li>Réalisé une grande partie de la CAO et des plans du boîtier de connecteurs.</li>
<li>Ajusté les rails et d'autres pièces pour un montage exact.</li>
</ul>""",

    xb_h="ARBALÈTE À|ARMEMENT INVERSÉ", xb_label="Arbalète à armement inversé",
    xb_ctx="Projet personnel, conçu et fabriqué de A à Z. Encore un prototype.",
    xb_cad="CAO", xb_proto="PROTOTYPE",
    xb_range="Comparer le modèle CAO et le premier prototype complet",
    xb_alt_cad="Modèle SolidWorks de l'arbalète, pièces en couleurs.",
    xb_alt_proto="Premier prototype complet de l'arbalète, debout dans un étau.",
    xb_body="""
<p class="keep">32 pièces en aluminium usinées sur CNC, troisième itération après un prototype en PETG et un autre en carbone stratifié.</p>
<h3>Pourquoi l'armement inversé</h3>
<p>Sur une arbalète à armement inversé, les branches pointent vers le tireur : la corde parcourt une plus grande course pour la même largeur, et la masse se rapproche de la poignée. Les cames et le mécanisme d'armement deviennent plus difficiles à concevoir, et c'est justement ce qui m'intéressait.</p>
<h3>Les choix</h3>
<p><b>Un seul modèle pilote tout.</b> L'assemblage SolidWorks est piloté par un fichier d'équations partagé : changer une cote met à jour toutes les pièces qui en dépendent.</p>
<p><b>Vérifier avant d'usiner l'aluminium.</b> Chaque nouvelle géométrie a été testée en POM-C ou imprimée en 3D avant l'usinage. Les branches sont en fibre de verre, prototypées en POM.</p>
<p><b>Un simulateur du mécanisme d'armement.</b> Je l'ai développé avec l'aide de l'IA : je modifie en direct la forme et la position des pièces, la cinématique se met à jour instantanément, et je teste des idées sans retourner dans la CAO.</p>
<p><b>L'usinage.</b> 32 pièces en aluminium 6061, 7075 et 5052, assemblées par 120 éléments de visserie. Parcours adaptatifs, montages multi-opérations, lubrification MQL.</p>""",
    xb_more=(("crossbow-cam", "Une came en aluminium usinée, avec son roulement, tenue dans la main.", "Une came, à la sortie de la machine."),
             ("crossbow-top", "Le prototype vu de dessus sur l'établi.", "Vue de dessus : les branches pointent vers l'arrière."),
             ("crossbow-lever", "Le levier d'armement vert imprimé, en cours d'utilisation.", "Le levier d'armement.")),

    hk_h="GRAPPIN EN ALUMINIUM", hk_label="Grappin en aluminium",
    hk_ctx='Projet personnel. Aluminium 6061 et pointe en laiton. <a href="https://www.esilv.fr/un-grappin-articule-un-projet-dinnovation-technique-concu-a-lesilv/">Article sur le site de l\'ESILV</a>.',
    hk_body="""
<p class="keep">Tourné et fraisé, avec des bras qui se replient le long du fût. L'idée est venue d'amis qui en voulaient un pour l'escalade.</p>
<h3>D'abord en conventionnel, puis en CNC</h3>
<p>J'ai fait la première version sur machines conventionnelles. Quand j'ai voulu des formes plus complexes, le professeur d'atelier m'a dit d'arrêter de passer des heures à faire à la main ce qu'une CNC fait mieux. Je l'ai donc redessiné pour la CNC et j'ai écrit la FAO moi-même : bras crantés, poignée moletée et pointe en laiton, pour l'esthétique et pour le poids en bas.</p>
<p>Tour et fraiseuse, CNC et conventionnels. Les bras sortent d'une plaque en parcours adaptatifs ; le fût est tourné entre pointes.</p>""",
    hk_imgs=(("hook-deployed", "Le grappin en aluminium tenu à la main, trois bras ouverts.", "Bras ouverts."),
             ("hook-folded", "Le grappin, bras repliés le long du fût.", "Bras repliés.")),
    hk_more=(("hook-cnc-manual", "La version CNC devant l'ancienne version faite en conventionnel.", "Version CNC devant, version conventionnelle derrière."),
             ("hook-lathe", "Le fût en cours de tournage sur un tour CNC, soutenu par la contre-pointe.", "Tournage du fût."),
             ("hook-arm", "Un bras à moitié usiné dans sa plaque d'aluminium.", "Un bras, à moitié usiné dans sa plaque."),
             ("hook-fea", "Étude statique Ansys d'un bras, colorée selon le coefficient de sécurité.", "Étude statique d'un bras sous Ansys.")),

    mg_h="GARDE-BOUE EN CARBONE", mg_label="Garde-boue en carbone",
    mg_body="Pour mon vélo électrique de 1 500 W : j'ai scanné le vélo avec une application sur téléphone, dessiné le garde-boue sur le scan, imprimé le moule en quatre sections et stratifié le carbone au contact.",
    mg_imgs=(("mudguard-scan", "Le garde-boue dessiné sur un scan 3D du vélo, en quatre sections de moule colorées."),
             ("mudguard-layup", "Stratification du carbone sur le moule imprimé."),
             ("mudguard-fitted", "Le garde-boue en carbone fini, sur la roue arrière.")),

    cn_h="RETROFIT CNC ET GGSENDER", cn_label="Retrofit CNC et GGSender",
    cn_body=f'J\'ai reconstruit ma fraiseuse CNC autour d\'un contrôleur FluidNC et d\'une broche de 1,5 kW refroidie par eau, pilotée en Modbus RS485. J\'ai ensuite créé <a href="{GGSENDER}">GGSender</a>, un fork du logiciel libre gSender développé avec l\'aide de l\'IA, pour revoir la séquence de changement d\'outil afin que les outils gardent toute leur longueur utile, et pour journaliser les échanges avec le contrôleur à des fins de diagnostic. La plupart des pièces de cette page sont sorties de cette machine.',
    cn_img=("cnc-machine", "La fraiseuse CNC dans son caisson insonorisé, des pièces d'arbalète sur l'établi et le logiciel de pilotage à l'écran."),

    cd_h="LA CARTE QUE VOUS|AVEZ SCANNÉE", cd_label="La carte que vous avez scannée",
    cd_ctx="Usinée dans une plaque d'aluminium sur cette même machine, finition brute. Le disque au centre est un ressort ortho-planaire, de la même famille que celui de l'accéléromètre.",
    cd_body="Voici le programme de gravure que j'ai écrit pour le verso de votre carte, rejoué : <b>25 354 lignes de G-code</b>, un seul outil à graver à 90°.",
    cd_replay="Rejouer",

    xp_h="EXPÉRIENCE",
    xp=[
        ("Ambiance Lumière, Alfortville", "JUILLET 2025 - SEPT. 2027", "Alternant ingénieur conception industrielle",
         ["Fabricant de luminaires architecturaux sur mesure, du prototype à la petite série.",
          "54 projets de luminaires haut de gamme, dont 19 menés seul, du cahier des charges client aux plans de fabrication. Parmi eux, un luminaire de façade produit à 300 exemplaires avec des fournisseurs en France et en Asie, et un luminaire pour la campagne de Noël 2025 d'une maison de mode de luxe.",
          "Mise en service de la fraiseuse CNC de l'entreprise et usinage de ses premières pièces.",
          "Luminaires pour Notre-Dame de Paris pendant sa restauration.",
          "Je conçois des outillages et des équipements de mesure sur mesure pour l'atelier. Un banc règle la distance entre une lentille et sa LED en tournant sa partie haute, et l'affiche sur des graduations gravées.",
          "Simulation thermique, mesures optiques, suivi des fournisseurs."],
         (("ambiance-notredame", "Escalier hélicoïdal en chêne sous la charpente médiévale d'une tour de Notre-Dame, éclairé par des luminaires linéaires dans la main courante et le long des poutres.", "Notre-Dame de Paris restaurée : l'éclairage des tours."),
          ("ambiance-belfry", "Une cloche en bronze dans son beffroi en bois à Notre-Dame, éclairée sous les poutres.", "Notre-Dame de Paris : le beffroi."),
          ("ambiance-showcase", "Vitrine pour une maison de mode de luxe : un papillon en topiaire constellé de points lumineux, un sac en son centre.", "Une vitrine pour une maison de mode de luxe."),
          ("ambiance-rig", "Banc imprimé tenant un ruban LED flexible sous une lumière magenta.", "Un banc de mesure : distance lentille-LED."),
          ("ambiance-4axis", "Un bloc usiné sur une fraiseuse 4 axes avec axe rotatif.", "Usinage 4 axes."),
          ("ambiance-cfd", "Lignes de courant de convection autour de deux dissipateurs : ailettes droites et anneaux concentriques.", "Étude de convection de deux dissipateurs."))),
        ("Pôle Léonard de Vinci", "2023 - 2024", "Auxiliaire ateliers et laboratoires, temps partiel",
         ["Maintenance des machines-outils de l'atelier, mise en place de dispositifs de sécurité, rédaction de documentation technique."], ()),
    ],

    ed_h="FORMATION ET OUTILS",
    ed="""
<p><b>ESILV, Paris-La Défense</b> : diplôme d'ingénieur, majeure Modélisation et mécanique numérique. De 2022 à 2027, en alternance depuis 2025. En 2027, neuf semaines de formation pratique au soudage à Dublin.</p>
<p>Je modélise sous SolidWorks et Fusion 360, et j'ai aussi travaillé sous CATIA, 3DEXPERIENCE et Onshape. Je programme la FAO sous Fusion 360, 3DEXPERIENCE et Vectric Aspire. Je fais du calcul par éléments finis sous Ansys et Abaqus, de la simulation thermique, je route des PCB sous KiCad, et j'écris en Python, MATLAB, C++ et C#.</p>
<p>À l'atelier : fraisage CNC 3 et 4 axes, tournage et fraisage CNC et conventionnels, montages d'usinage, composites carbone, moulage résine, impression FDM et SLA, maintenance des machines.</p>
<p>Français (langue maternelle), anglais C1 (TOEFL ITP 663/677), allemand (notions).</p>""",

    ct_h="CONTACT",
    ct="Je cherche un CDI d'ingénieur fabrication, industrialisation ou méthodes à partir de septembre 2027, en Île-de-France.",
    colophon="Les titres utilisent les vrais traits gravés sur la carte, extraits de ses fichiers de conception. Le texte est en Atkinson Hyperlegible Next.",
    nf_title="Page introuvable", nf="Cette page n'existe pas. Le QR code de la carte mène à la page d'accueil.", nf_link="Aller à l'accueil",
)


# ---------------------------------------------------------------- page
def head(c, canonical, robots=""):
    p = c["prefix"]
    alt_en, alt_fr = URL, URL + "fr/"
    return f"""<!doctype html>
<html lang="{c['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(c['title'])}</title>
<meta name="description" content="{html.escape(c['desc'])}">
{robots}<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="fr" href="{alt_fr}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(c['title'])}">
<meta property="og:description" content="{html.escape(c['desc'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{URL}assets/og.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#d4d7db">
<link rel="icon" href="{p}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{p}assets/apple-touch-icon.png">
<link rel="preload" href="{p}assets/fonts/atkinson-next.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/css/site.css?v={ver("assets/css/site.css")}">
</head>"""


def page(c):
    p = c["prefix"]
    S = lambda n, a, cap=None: fig(n, a, cap, row_sizes(n), prefix=p)
    call = c["cs_call"]
    tb = "".join(f'<div><dt>{k}</dt><dd>{L(v, weight=1/11)}<span class="u">{u}</span></dd></div>' for k, v, u in c["tb"])
    xp = []
    for name_, when, role, items, imgs in c["xp"]:
        pics = "".join(f'<figure class="{"portrait" if n == "portrait" else ""}">{img(n, a, row_sizes(n) if len(imgs) > 1 else "(min-width: 1000px) 30vw, 90vw", prefix=p)}{f"<figcaption>{cp}</figcaption>" if cp else ""}</figure>' for n, a, cp in imgs)
        strip = f'<div class="strip" tabindex="0" role="group" aria-label="Photos">{pics}</div>' if len(imgs) > 1 else pics
        xp.append(f"""<article>
<span class="when">{L(when, weight=1/10)}</span>
<h3>{name_}</h3>
<p class="role">{role}</p>
<ul>{''.join(f'<li>{i}</li>' for i in items)}</ul>
{strip}
</article>""")
    body = f"""
<body>
<header class="wrap hero">
  <div class="bar"><span class="lbl">{L("GG-2027-001  REV C", weight=1/10, label=c['part'])}</span><a href="{c['other']}" hreflang="{c['other_lang']}" lang="{c['other_lang']}">{c['other_label']}</a></div>
  <h1 class="name">{L("GABRIEL|GHANEM", weight=1/15, track=1.6, lead=1.42, label="Gabriel Ghanem")}</h1>
  <div class="intro">
    <figure class="me">{img("portrait", c['me_alt'], "(min-width: 1000px) 34vw, 34vw", eager=True, prefix=p)}</figure>
    <p class="lead">{c['lead']}</p>
  </div>
  <p class="avail">{c['avail']}</p>
  <nav class="links" aria-label="Contact"><a href="mailto:{EMAIL}">{c['email']}</a><a href="{LINKEDIN}">LinkedIn</a><a href="{p}{c['cvfile']}">{c['cv']}</a></nav>
  <p class="jump">{c['jump']}</p>
</header>

<main>
<section class="wrap project feature" id="cubesat" aria-labelledby="h-cubesat">
  <figure class="callouts bleed">
    {img("cubesat-section", c['cs_alt'], "(min-width: 1000px) 55vw, 100vw", prefix=p)}
    <svg class="leaders" viewBox="0 0 976 945" preserveAspectRatio="none" aria-hidden="true">
      <g stroke="#0f1113" stroke-width="2" fill="none" vector-effect="non-scaling-stroke"><path vector-effect="non-scaling-stroke" d="M497,418 L700,330 L770,330"/><path vector-effect="non-scaling-stroke" d="M600,478 L720,560 L800,560"/><path vector-effect="non-scaling-stroke" d="M180,470 L120,560 L40,560"/></g>
      <g fill="#0f1113"><circle cx="497" cy="418" r="7"/><circle cx="600" cy="478" r="7"/><circle cx="180" cy="470" r="7"/></g>
    </svg>
    <span class="callout" style="left:75%;top:31%">{L(call[0], weight=1/9)}</span>
    <span class="callout" style="left:78%;top:56.5%">{L(call[1], weight=1/9)}</span>
    <span class="callout" style="left:3%;top:56.5%">{L(call[2], weight=1/9)}</span>
  </figure>
  <div class="head"><h2 id="h-cubesat">{L(c['cs_h'], track=0.5, label=c['cs_label'])}</h2><p class="ctx">{c['cs_ctx']}</p></div>
  <p class="summary">{c['cs_sum']}</p>
  <dl class="tb" aria-label="{c['tb_label']}">{tb}</dl>
  <div class="prose">
    <figure>
      {img("cubesat-spring", c['spring_alt'], "(min-width: 1000px) 40vw, 100vw", prefix=p)}
      <div class="spec" role="img" aria-label="{html.escape(c['spring_spec'])}">
        <span class="fcf"><span><svg width="18" height="14" viewBox="0 0 18 14" aria-hidden="true"><path d="M3,13 L9,1 M9,13 L15,1" stroke="#3f454c" stroke-width="1.6" fill="none"/></svg></span><span>{L("0.02" if c['lang'] == 'en' else "0,02", weight=1/10, label="")}</span><span>{L("A", weight=1/10, label="")}</span></span>
        <span class="lbl">{L("ISO 10579-NR", weight=1/10, label="")}</span>
        <span class="ra"><svg width="30" height="18" viewBox="0 0 30 18" aria-hidden="true"><path d="M1,9 L5,17 L13,1 H29" stroke="#3f454c" stroke-width="1.5" fill="none"/></svg>{L("Ra 0.8" if c['lang'] == 'en' else "Ra 0,8", weight=1/10, label="")}</span>
      </div>
      <figcaption>{c['spring_cap']}</figcaption>
    </figure>
    {fold(c['cs_body'])}
  </div>
  <div class="media">
    <div class="pair">{fig(c['cs_proto'][0], c['cs_proto'][1], c['cs_proto'][2], "(min-width: 1000px) 22vw, 46vw", prefix=p)}{fig(c['cs_final'][0], c['cs_final'][1], c['cs_final'][2], "(min-width: 1000px) 22vw, 46vw", prefix=p)}</div>
    <div class="strip" tabindex="0" role="group" aria-label="Photos">{''.join(S(n, a, cp) for n, a, cp in c['cs_more'])}</div>
  </div>
</section>

<section class="wrap project split" id="leofly" aria-labelledby="h-leofly">
  <div class="head"><h2 id="h-leofly">{L(c['lf_h'], track=0.5, label=c['lf_label'])}</h2><p class="ctx">{c['lf_ctx']}</p></div>
  <div class="prose">{fold(c['lf_body'])}</div>
  <figure>{img("leofly-teach-group", c['lf_group'][0], "(min-width: 1000px) 45vw, 100vw", prefix=p)}<figcaption>{c['lf_group'][1]}</figcaption></figure>
  <div class="media" style="grid-column:1/-1"><div class="strip" tabindex="0" role="group" aria-label="Photos">{''.join(S(n, a, cp) for n, a, cp in c['lf_more'])}</div></div>
</section>

<section class="wrap project split" id="crossbow" aria-labelledby="h-crossbow">
  <div class="head"><h2 id="h-crossbow">{L(c['xb_h'], track=0.5, label=c['xb_label'])}</h2><p class="ctx">{c['xb_ctx']}</p></div>
  <div class="compare" style="--pos:50%">
    <img src="{p}assets/img/crossbow-proto-490.webp" width="490" height="841" alt="{html.escape(c['xb_alt_proto'])}" loading="lazy">
    <img class="top" src="{p}assets/img/crossbow-cad-490.webp" width="490" height="841" alt="{html.escape(c['xb_alt_cad'])}" loading="lazy">
    <span class="tag" style="left:10px">{L(c['xb_cad'], weight=1/10, label="")}</span><span class="tag" style="right:10px">{L(c['xb_proto'], weight=1/10, label="")}</span>
    <input type="range" min="0" max="100" value="50" aria-label="{html.escape(c['xb_range'])}">
    <span class="line" aria-hidden="true"></span>
  </div>
  <div class="prose">{fold(c['xb_body'])}</div>
  <div class="media" style="grid-column:1/-1"><div class="strip" tabindex="0" role="group" aria-label="Photos">{''.join(S(n, a, cp) for n, a, cp in c['xb_more'])}</div></div>
</section>

<section class="wrap project split" id="hook" aria-labelledby="h-hook">
  <div class="head"><h2 id="h-hook">{L(c['hk_h'], track=0.5, label=c['hk_label'])}</h2><p class="ctx">{c['hk_ctx']}</p></div>
  <div class="pair">{''.join(fig(n, a, cp, "(min-width: 1000px) 22vw, 46vw", prefix=p) for n, a, cp in c['hk_imgs'])}</div>
  <div class="prose">{fold(c['hk_body'])}</div>
  <div class="media" style="grid-column:1/-1"><div class="strip" tabindex="0" role="group" aria-label="Photos">{''.join(S(n, a, cp) for n, a, cp in c['hk_more'])}</div></div>
</section>

<section class="wrap minor" id="mudguard" aria-labelledby="h-mudguard">
  <div class="head"><h2 id="h-mudguard">{L(c['mg_h'], track=0.5, label=c['mg_label'])}</h2></div>
  <p class="summary">{c['mg_body']}</p>
  <div class="thumbs" tabindex="0" role="group" aria-label="Photos">{''.join(img(n, a, row_sizes(n, 240), prefix=p) for n, a in c['mg_imgs'])}</div>
</section>

<section class="wrap minor split" id="cnc" aria-labelledby="h-cnc">
  <div class="head"><h2 id="h-cnc">{L(c['cn_h'], track=0.5, label=c['cn_label'])}</h2></div>
  <p class="summary">{c['cn_body']}</p>
  <figure>{img(c['cn_img'][0], c['cn_img'][1], "(min-width: 1000px) 45vw, 100vw", prefix=p)}</figure>
</section>

<section class="bed" id="card" aria-labelledby="h-card">
  <div class="wrap inner">
    <div class="head"><h2 id="h-card">{L(c['cd_h'], track=0.5, label=c['cd_label'])}</h2><p class="ctx">{c['cd_ctx']}</p></div>
    <div>
      <div class="plate"><canvas id="toolpath" data-src="{p}assets/data/verso-toolpath.json" role="img" aria-label="{'The engraving toolpath of the card back, drawn line by line.' if c['lang'] == 'en' else 'Le parcours de gravure du verso de la carte, tracé ligne à ligne.'}"></canvas></div>
      <div class="dro"><span id="dro-xy" aria-hidden="true" style="font-variant-numeric:tabular-nums;font-size:.85rem"></span><button type="button" id="replay">{c['cd_replay']}</button></div>
    </div>
    <p>{c['cd_body']}</p>
  </div>
</section>

<section class="wrap project" id="experience" aria-labelledby="h-xp">
  <div class="head"><h2 id="h-xp">{L(c['xp_h'], track=0.5)}</h2></div>
  <div class="xp">{''.join(xp)}</div>
</section>

<section class="wrap project" id="education" aria-labelledby="h-ed">
  <div class="head"><h2 id="h-ed">{L(c['ed_h'], track=0.5)}</h2></div>
  <div class="facts">{c['ed']}</div>
</section>

<section class="wrap contact" id="contact" aria-labelledby="h-ct">
  <div class="head"><h2 id="h-ct">{L(c['ct_h'], track=0.5)}</h2></div>
  <p class="summary">{c['ct']}</p>
  <p class="big"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p class="links"><a href="{LINKEDIN}">LinkedIn</a><a href="{p}{c['cvfile']}">{c['cv']}</a></p>
</section>
</main>

<footer><div class="wrap"><p class="colo">{c['colophon']}</p><p>Gabriel Ghanem, 2026</p></div></footer>
<script src="{p}assets/js/site.js?v={ver("assets/js/site.js")}" defer></script>
</body>
</html>
"""
    out = head(c, URL if c["lang"] == "en" else URL + "fr/") + body
    return fr_typo(out) if c["lang"] == "fr" else out


def not_found():
    c = T["en"]; f = T["fr"]; base = "/CNC-Business-card-/"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{c['nf_title']}: Gabriel Ghanem</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}assets/css/site.css?v={ver("assets/css/site.css")}">
</head>
<body>
<main class="wrap hero" style="min-height:70vh;align-content:center">
  <p class="name" style="--cap:clamp(40px,14vw,110px)">{L("404", weight=1/14, label="404")}</p>
  <p class="lead">{c['nf']}</p>
  <p class="links"><a href="{base}">{c['nf_link']}</a></p>
  <p lang="fr" class="avail">{fr_typo(f['nf'])} <a href="{base}fr/">{f['nf_link']}</a></p>
</main>
</body>
</html>
"""


def favicon():
    """The card's spring: pocket, three spiral slots (generate.py: r 6.2 to 11.8 mm, 205 degrees), boss."""
    import math
    def spiral(phase):
        pts = []
        for i in range(41):
            a = math.radians(phase + 205 * i / 40); r = 6.2 + (11.8 - 6.2) * i / 40
            pts.append(f"{r * math.cos(a):.2f},{r * math.sin(a):.2f}")
        return "M" + " L".join(pts)
    slots = "".join(f'<path d="{spiral(k * 120 - 90)}"/>' for k in range(3))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -14 28 28"><circle r="13.6" fill="#c9cdd2" stroke="#3f454c" stroke-width=".8"/>'
            f'<g fill="none" stroke="#0f1113" stroke-width="1.9" stroke-linecap="round">{slots}</g><circle r="4.6" fill="#e6e8eb" stroke="#3f454c" stroke-width=".6"/></svg>')


if __name__ == "__main__":
    (DOCS / "index.html").write_text(page(T["en"]), encoding="utf-8")
    (DOCS / "fr").mkdir(exist_ok=True)
    (DOCS / "fr/index.html").write_text(page(T["fr"]), encoding="utf-8")
    (DOCS / "404.html").write_text(not_found(), encoding="utf-8")
    (DOCS / "favicon.svg").write_text(favicon(), encoding="utf-8")
    print("built", [str(p.relative_to(ROOT)) for p in (DOCS / "index.html", DOCS / "fr/index.html", DOCS / "404.html")])
