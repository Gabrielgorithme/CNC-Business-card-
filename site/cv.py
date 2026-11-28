"""One-page CVs (EN, FR) for the site, anonymised: no phone, no address, no client brands.

    python3 site/cv.py            -> site/out/cv-en.html, cv-fr.html
    node site/print-cv.js         -> docs/assets/cv/gabriel-ghanem-cv-{en,fr}.pdf"""
import pathlib
import isocp
from build import fr_typo, EMAIL, LINKEDIN, URL

OUT = pathlib.Path(__file__).resolve().parent / "out"
FONT = (pathlib.Path(__file__).resolve().parent.parent / "docs/assets/fonts/atkinson-next.woff2").as_uri()

CV = {
"en": dict(
    role="Mechanical engineering student, work-study. Manufacturing, industrialisation, design.",
    line=f"{EMAIL} · linkedin.com/in/gabriel-ghanem-02528a208 · Paris area · Driving licence B",
    avail="Available for a permanent job (CDI) from September 2027.",
    h=("PROFILE", "EXPERIENCE", "ROCKETRY CLUB", "PERSONAL PROJECTS", "EDUCATION", "SKILLS", "LANGUAGES"),
    profile="Final-year engineering student at ESILV (major in modelling and computational mechanics), in a work-study position in industrial design at a custom lighting manufacturer. Hands-on: from the CAD model to the machined part, through CAM, tooling and manufacturing drawings. Looking for a manufacturing, industrialisation or methods engineering job from September 2027.",
    xp=[("Industrial design engineer, work-study: Ambiance Lumière", "July 2025 to Sept. 2027",
         "Alfortville. Custom architectural lighting, from prototype to small series.",
         ["54 high-end luminaire projects, 19 of them carried alone from the client's brief to the manufacturing drawings.",
          "Design in SolidWorks and Fusion 360; drawings and manufacturing files sent to subcontractors.",
          "Product validation by thermal simulation and optical measurement; supplier follow-up.",
          "In-house workshop tooling; commissioned the company's CNC mill and machined its first parts.",
          "Lead project: a luminaire for a luxury fashion house's 2025 Christmas campaign."]),
        ("Workshop and lab assistant (part-time): Pôle Léonard de Vinci", "2023 to 2024", "",
         ["Maintained the workshop's machine tools, installed safety devices, wrote technical documentation."])],
    club=[("Léofly, experimental rockets", "2023 to today", "Rockets and payloads for the C'Space (CNES) and EuRoC campaigns.",
           ["Design and manufacturing referent (2026 to today): technical support to the teams; brought in as an expert on the STAR-D experiment (REXUS sounding rocket): machined its aluminium housing and custom TPU seals with no catalogue equivalent.",
            "Technical director, in charge of manufacturing (2024 to 2026): led the teams on the Krypton rocket; ran the CAD, CAM and machine-tool training; machined aluminium structure rings, steel and PMMA parts; carbon composite structures.",
            "Designer, CubeSat project (2023 to 2026): magnetic accelerometer: mechanics, PCB in KiCad, signal processing, FEA.",
            "Member, Xénon rocket (2023): CAD, CAM and FEA in a project team.",
            "Also: maths and mechanics tutor at LeoLearning, ESILV's tutoring club."])],
    proj=[("Reverse-draw crossbow, designed and built from scratch", "",
           ["32 CNC-machined aluminium parts (6061, 7075, 5052), 120 fasteners; third iteration after PETG and laminated carbon prototypes.",
            "Parametric SolidWorks model (shared equations file); CAM and machining: adaptive toolpaths, multi-operation fixtures, MQL; geometries checked in POM-C and 3D printing first.",
            "Cocking-mechanism simulator built with AI assistance: live-editable parts, kinematics recomputed instantly."]),
          ("GGSender, CNC control software adapted with AI assistance", "",
           ["Fork of the open-source gSender, versioned on GitHub: tool-change sequence reworked to preserve tool length, persistent log of controller traffic for diagnosis."]),
          ("Also", "", ["Full retrofit of a CNC router (FluidNC controller, water-cooled 1.5 kW spindle driven by a VFD over Modbus RS485); 1,500 W electric bike with a carbon mudguard; resin and composite moulds; machined aluminium grappling hook."])],
    edu=[("Engineering degree (diplôme d'ingénieur), major in modelling and computational mechanics: ESILV", "2022 to 2027",
          "Paris-La Défense. Work-study engineering cycle (2025 to 2027). 2027 international mobility: nine weeks of hands-on welding training in Dublin, Ireland."),
         ("French baccalauréat, maths (with advanced maths) and physics-chemistry", "2022", "")],
    skills=["Manufacturing: 3-axis CNC milling, turning, fixtures, carbon composites, resin casting, FDM and SLA printing, machine maintenance.",
            "CAD and drawings: SolidWorks, CATIA, 3DEXPERIENCE, Fusion 360, Onshape; drawings and manufacturing files.",
            "CAM: Fusion 360, 3DEXPERIENCE, Vectric Aspire. Simulation: Ansys, Abaqus (FEA), thermal simulation.",
            "Electronics and code: KiCad, Python, C++, C#, MATLAB, Git; AI-assisted tool development."],
    lang="French (native), English C1 (TOEFL ITP 663/677), German (basics). Interests: running, speedcubing, woodworking.",
    site="Portfolio: " + URL,
),
"fr": dict(
    role="Élève ingénieur mécanique en alternance. Fabrication, industrialisation, conception.",
    line=f"{EMAIL} · linkedin.com/in/gabriel-ghanem-02528a208 · Île-de-France · Permis B",
    avail="Disponible en CDI à partir de septembre 2027.",
    h=("PROFIL", "EXPÉRIENCE PROFESSIONNELLE", "EXPÉRIENCE ASSOCIATIVE", "PROJETS PERSONNELS", "FORMATION", "COMPÉTENCES TECHNIQUES", "LANGUES"),
    profile="Élève ingénieur en dernière année à l'ESILV (majeure Modélisation et mécanique numérique), en alternance en conception industrielle chez un fabricant de luminaires sur mesure. Profil terrain : du modèle CAO à la pièce usinée, en passant par la FAO, l'outillage et les plans de fabrication. Recherche un poste d'ingénieur fabrication, industrialisation ou méthodes à partir de septembre 2027.",
    xp=[("Alternant ingénieur conception industrielle : Ambiance Lumière", "juil. 2025 – sept. 2027",
         "Alfortville. Fabricant de luminaires architecturaux sur mesure, du prototype à la petite série.",
         ["54 projets de luminaires haut de gamme, dont 19 menés en autonomie complète, du cahier des charges client aux plans de fabrication.",
          "Conception sous SolidWorks et Fusion 360, mises en plan et dossiers de fabrication transmis aux sous-traitants.",
          "Validation produit par simulations thermiques et mesures optiques ; suivi des relations fournisseurs.",
          "Conception d'outillages internes pour l'atelier ; mise en service de la fraiseuse CNC de l'entreprise et usinage des premières pièces.",
          "Projet phare : luminaire pour la campagne de Noël 2025 d'une maison de mode de luxe."]),
        ("Auxiliaire ateliers et laboratoires (temps partiel) : Pôle Léonard de Vinci", "2023 – 2024", "",
         ["Maintenance des machines-outils de l'atelier, mise en place de dispositifs de sécurité et rédaction de documentation technique."])],
    club=[("Léofly, association de fusées expérimentales", "2023 – aujourd'hui", "Fusées et charges utiles pour les campagnes C'Space (CNES) et EuRoC.",
           ["Référent conception et fabrication (2026 – auj.) : appui technique aux équipes ; sollicité comme expert sur l'expérience STAR-D (fusée-sonde REXUS) : usinage du boîtier en aluminium et joints d'étanchéité TPU sur mesure, sans équivalent catalogue.",
            "Directeur technique, responsable fabrication (2024 – 2026) : direction technique et encadrement des équipes de la fusée Krypton ; direction des formations CAO, FAO et machines-outils ; usinage des bagues de structure en aluminium, pièces acier et PMMA ; structures en composite carbone.",
            "Concepteur, projet CubeSat (2023 – 2026) : accéléromètre magnétique : mécanique, PCB sous KiCad, traitement du signal, calcul FEA.",
            "Membre, fusée Xénon (2023) : CAO, FAO et calcul FEA au sein d'une équipe projet.",
            "Aussi : tuteur en mathématiques et mécanique à LeoLearning, l'association de tutorat de l'ESILV."])],
    proj=[("Arbalète à armement inversé, conception et fabrication complètes", "",
           ["32 pièces en aluminium usinées sur CNC (6061, 7075, 5052), 120 éléments de visserie ; troisième itération après deux prototypes en PETG puis en carbone stratifié.",
            "Modèle SolidWorks paramétré (fichier d'équations partagé) ; FAO et usinage : parcours adaptatifs, montages multi-opérations, lubrification MQL ; géométries validées en POM-C et impression 3D avant usinage.",
            "Simulateur du mécanisme d'armement développé avec l'IA : pièces modifiables en direct, cinématique recalculée instantanément."]),
          ("GGSender, logiciel de pilotage CNC adapté avec l'IA", "",
           ["Fork du logiciel libre gSender, versionné sous GitHub : séquence de changement d'outil revue pour préserver la longueur utile des outils, journalisation persistante des échanges avec le contrôleur."]),
          ("Aussi", "", ["Retrofit complet d'une fraiseuse CNC (contrôleur FluidNC, broche 1,5 kW refroidie par eau, variateur en Modbus RS485) ; vélo électrique 1 500 W avec garde-boue en carbone ; moules pour résine et composites ; grappin en aluminium usiné."])],
    edu=[("Diplôme d'ingénieur, majeure Modélisation et mécanique numérique : ESILV", "2022 – 2027",
          "Paris-La Défense. Cycle ingénieur en alternance (2025 – 2027). Mobilité internationale 2027 : formation pratique au soudage à Dublin, Irlande (9 semaines)."),
         ("Baccalauréat général, spécialités mathématiques (maths expertes) et physique-chimie", "2022", "")],
    skills=["Fabrication : usinage CNC 3 axes, tournage, montages d'usinage, composites carbone, moulage résine, impression 3D FDM et SLA, maintenance machines-outils.",
            "CAO et plans : SolidWorks, CATIA, 3DEXPERIENCE, Fusion 360, Onshape ; mises en plan et dossiers de fabrication.",
            "FAO : Fusion 360, 3DEXPERIENCE, Vectric Aspire. Simulation : Ansys, Abaqus (éléments finis), simulation thermique.",
            "Électronique et code : KiCad, Python, C++, C#, MATLAB, Git ; développement d'outils assisté par IA."],
    lang="Français (natif), anglais C1 (TOEFL ITP 663/677), allemand (notions). Intérêts : course à pied, speedcubing, menuiserie.",
    site="Portfolio : " + URL,
)}


def h(t): return f'<h2><span class="sr">{t}</span>{isocp.svg(t, weight=1/10, track=0.6)}</h2>'


def entry(title, when, sub, items):
    w = f'<span class="when">{when}</span>' if when else ""
    s = f'<p class="sub">{sub}</p>' if sub else ""
    li = "".join(f"<li>{i}</li>" for i in items)
    return f'<div class="e"><div class="t"><b>{title}</b>{w}</div>{s}<ul>{li}</ul></div>'


def doc(lang):
    c = CV[lang]
    html = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>Gabriel Ghanem CV</title>
<style>
@font-face {{ font-family: A; src: url("{FONT}") format("woff2"); font-weight: 200 800; }}
@page {{ size: A4; margin: 9mm 12mm 8mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font: 400 8.05pt/1.3 A, sans-serif; color: #0f1113; }}
.sr {{ position: absolute; left: -9999px; }}
.isocp {{ display: block; height: calc(var(--cap) * var(--h)); width: auto; aspect-ratio: var(--ar); overflow: visible; }}
header {{ display: grid; gap: 1.6mm; border-bottom: 1.2pt solid #3f454c; padding-bottom: 2.6mm; }}
header .n {{ --cap: 17pt; color: #3f454c; }}
header p {{ margin: 0; }}
.role {{ font-size: 10pt; font-weight: 700; }}
.line {{ color: #3f454c; }}
h2 {{ margin: 2.6mm 0 1.1mm; --cap: 6.6pt; color: #3f454c; border-bottom: .6pt solid #6f767f; padding-bottom: 1mm; }}
.e {{ margin-bottom: 1.3mm; break-inside: avoid; }}
.t {{ display: flex; justify-content: space-between; gap: 4mm; }}
.when {{ color: #3f454c; white-space: nowrap; }}
.sub {{ margin: .3mm 0; color: #3f454c; font-style: italic; }}
ul {{ margin: .6mm 0 0; padding-left: 3.6mm; }}
li {{ margin-bottom: .25mm; }}
p {{ margin: 0 0 1mm; }}
.foot {{ margin-top: 3mm; color: #3f454c; font-size: 7.6pt; }}
</style></head><body>
<header>
  <div class="n"><span class="sr">Gabriel Ghanem</span>{isocp.svg("GABRIEL GHANEM", weight=1/13, track=1.4)}</div>
  <p class="role">{c['role']}</p>
  <p class="line">{c['line']}</p>
  <p><b>{c['avail']}</b></p>
</header>
{h(c['h'][0])}<p>{c['profile']}</p>
{h(c['h'][1])}{''.join(entry(*x) for x in c['xp'])}
{h(c['h'][2])}{''.join(entry(*x) for x in c['club'])}
{h(c['h'][3])}{''.join(entry(t, w, '', i) for t, w, i in c['proj'])}
{h(c['h'][4])}{''.join(f'<div class="e"><div class="t"><b>{t}</b><span class="when">{w}</span></div>{f"<p class=sub>{s}</p>" if s else ""}</div>' for t, w, s in c['edu'])}
{h(c['h'][5])}<ul>{''.join(f'<li>{s}</li>' for s in c['skills'])}</ul>
{h(c['h'][6])}<p>{c['lang']}</p>
<p class="foot">{c['site']}</p>
</body></html>"""
    return fr_typo(html) if lang == "fr" else html


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for lang in ("en", "fr"):
        (OUT / f"cv-{lang}.html").write_text(doc(lang), encoding="utf-8")
    print("written", [p.name for p in OUT.glob("cv-*.html")])
