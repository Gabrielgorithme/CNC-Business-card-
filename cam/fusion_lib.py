"""Shared helpers for the Fusion scripts that build the Card v3 CAM (run through the Fusion MCP).
Each build script is this file + a `run` function, sent as one script."""
import adsk.core, adsk.fusion, adsk.cam, os, re, time, math

CHECK = r'C:\Users\gabri\OneDrive\Business Card\cam\check_v3'
LIB = 'hub://GAB/Library.hub'
L, WD = 85.6, 53.98
HEIGHTS = (('clearanceHeight_mode', "'from retract height'"), ('clearanceHeight_offset', '4 mm'),
           ('retractHeight_mode', "'from stock top'"), ('retractHeight_offset', '1 mm'))

def pump(n=5):
    for _ in range(n):
        adsk.doEvents(); time.sleep(0.05)

def ctx():
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if 'Card v3' not in doc.name:
        raise RuntimeError('unexpected active document ' + doc.name)
    des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    cam = adsk.cam.CAM.cast(doc.products.itemByProductType('CAMProductType'))
    rc = des.rootComponent
    return app, doc, rc, rc.allOccurrences.item(0).bRepBodies.item(0), cam

def tools():
    lib = adsk.cam.CAMManager.get().libraryManager.toolLibraries.toolLibraryAtURL(adsk.core.URL.create(LIB))
    out = {}
    for n, kind in ((60, 'flat end mill'), (20, 'flat end mill'), (10, 'flat end mill'), (43, 'chamfer mill'), (31, 'ball end mill')):
        for i in range(lib.count):
            t = lib.item(i)
            if t.parameters.itemByName('tool_number').value.value == n and t.parameters.itemByName('tool_type').value.value == kind:
                out[n] = t
    return out

def setp(P, pairs):
    for n, e in pairs:
        p = P.itemByName(n)
        if p is None: raise RuntimeError('no parameter ' + n)
        p.expression = e

def feeds(P, cut, plunge, ramp=None):
    setp(P, (('tool_spindleSpeed', '24000 rpm'), ('tool_feedCutting', '%g mm/min' % cut), ('tool_feedEntry', '%g mm/min' % cut),
             ('tool_feedExit', '%g mm/min' % cut), ('tool_feedPlunge', '%g mm/min' % plunge)))
    if P.itemByName('tool_feedRamp'): P.itemByName('tool_feedRamp').expression = '%g mm/min' % (ramp or plunge)

def sketch(rc, name):
    s = rc.sketches.itemByName(name)
    if s is None: raise RuntimeError('no sketch ' + name)
    return s

def select_sketches(op, pname, sketches):
    cv = op.parameters.itemByName(pname).value
    cs = cv.getCurveSelections(); cs.clear()
    for s in sketches:
        sel = cs.createNewSketchSelection(); sel.inputGeometry = [s]
    cv.applyCurveSelections(cs)

def select_chains(op, pname, groups, reverted):
    cv = op.parameters.itemByName(pname).value
    cs = cv.getCurveSelections(); cs.clear()
    for g in groups:
        ch = cs.createNewChainSelection(); ch.inputGeometry = g; ch.isReverted = reverted
    cv.applyCurveSelections(cs)

def curves(s):
    return [c for c in s.sketchCurves]

def generate(cam, op, timeout=600):
    t = time.time()
    fut = cam.generateToolpath(op)
    while not fut.isGenerationCompleted and time.time() - t < timeout:
        adsk.doEvents(); time.sleep(0.1)
    return fut.isGenerationCompleted

def post_stats(cam, op, tag, to_model):
    """Posts one operation with the user's grbl post and summarises where the tool cuts, in MODEL x/y (mm)."""
    os.makedirs(CHECK, exist_ok=True)
    pi = adsk.cam.PostProcessInput.create(tag, os.path.join(cam.personalPostFolder, 'grbl.cps'), CHECK, adsk.cam.PostOutputUnitOptions.MillimetersOutput)
    pi.isOpenInEditor = False
    cam.postProcess(op, pi)
    txt = open(os.path.join(CHECK, tag + '.nc')).read()
    x = y = 0.0; z = 15.0; pts = []
    for line in txt.splitlines():
        line = re.sub(r'\(.*?\)', '', line)
        if 'G28' in line: continue
        w = dict(re.findall(r'([XYZ])(-?\d*\.?\d+)', line))
        if not w: continue
        x = float(w.get('X', x)); y = float(w.get('Y', y)); z = float(w.get('Z', z))
        if z < -0.0005: pts.append((to_model(x, y), z))
    if not pts: return {'n': 0}
    xs = [p[0][0] for p in pts]; ys = [p[0][1] for p in pts]; zs = [p[1] for p in pts]
    return {'n': len(pts), 'x': (round(min(xs), 2), round(max(xs), 2)), 'y': (round(min(ys), 2), round(max(ys), 2)),
            'z': (round(min(zs), 3), round(max(zs), 3)), 'pts': pts, 'feeds': sorted(set(re.findall(r'F(\d+\.?\d*)', txt)), key=float)}

def report(cam, op, st):
    mt = cam.getMachiningTime(op, 100, 3000, 0)
    w = op.warning.strip().replace('\n', ' ')[:140]
    print('%-34s T%-3d valid %s | %4d s | cut pts %5d | X %s Y %s Z %s | F %s%s' % (op.name[:34], op.tool.parameters.itemByName('tool_number').value.value, op.isToolpathValid, mt.machiningTime, st.get('n', 0), st.get('x'), st.get('y'), st.get('z'), st.get('feeds'), (' | WARN ' + w) if w else ''))

def radial(st, cx, cy):
    r = [math.hypot(p[0][0] - cx, p[0][1] - cy) for p in st['pts']]
    return round(min(r), 3), round(max(r), 3)
