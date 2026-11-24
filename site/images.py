"""Export the site's images from the source photos (kept out of the repo) into docs/assets/img.

    python3 site/images.py <source-assets dir> <uploads dir>

Every image gets WebP variants at a few widths for srcset; crops remove garage clutter.
The REXUS module photo is only ever taken from its face-cropped version."""
import json, pathlib, sys
from PIL import Image, ImageOps

SRC, UP = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

# name: (source, crop box or None, widths)
IMAGES = {
    "cubesat-section": (SRC / "01-cubesat-accelerometer/2-cad-render-section.webp", None, (640, 976)),
    "cubesat-final":   (SRC / "01-cubesat-accelerometer/5-final-product.webp", None, (480, 953)),
    "cubesat-pcbs":    (SRC / "01-cubesat-accelerometer/3-pcbs.webp", None, (400, 532)),
    "cubesat-spring":  (SRC / "01-cubesat-accelerometer/7-spring.webp", (0, 230, 709, 945), (480, 709)),
    "cubesat-proto":   (SRC / "01-cubesat-accelerometer/1-prototype-v1-red-table.webp", None, (480, 926)),
    "cubesat-tank":    (SRC / "01-cubesat-accelerometer/6-pmma-oil-tank.webp", None, (400, 532)),
    "cubesat-talk":    (SRC / "01-cubesat-accelerometer/4-talk.webp", None, (640, 1200)),
    "stard-tank":      (SRC / "04-rexus-stard/2-pcm-tank.webp", None, (480, 709)),
    "stard-module":    (SRC / "04-rexus-stard/1-module-crop.webp", None, (480, 709)),
    "crossbow-cad":    (SRC / "03-crossbow/1-cad.png", None, (490,)),
    "crossbow-proto":  (SRC / "03-crossbow/2-proto-front.webp", (68, 66, 546, 895), (490,)),
    "crossbow-cam":    (SRC / "03-crossbow/3-cam.webp", (0, 60, 709, 945), (480, 709)),
    "crossbow-top":    (SRC / "03-crossbow/4-proto-top.webp", (0, 190, 709, 720), (480, 709)),
    "crossbow-lever":  (SRC / "03-crossbow/5-lever.webp", (0, 120, 709, 945), (480, 709)),
    "hook-deployed":   (UP / "87f2da8de536e18cd5def6a3f862a54a.png", (40, 300, 1320, 1961), (480, 960)),
    "hook-folded":     (UP / "b5130b8e2caeb78f328fd56872b955d5.png", None, (480, 960)),
    "hook-cnc-manual": (SRC / "02-grappling-hook/3-cnc-vs-man.webp", None, (480, 955)),
    "hook-lathe":      (SRC / "02-grappling-hook/1-lathe.webp", None, (640, 1260)),
    "hook-arm":        (SRC / "02-grappling-hook/2-arm-half.webp", None, (480, 709)),
    "mudguard-scan":   (SRC / "05-mudguard/1-scan-cad.png", None, (480, 720)),
    "mudguard-layup":  (SRC / "05-mudguard/3-layup.webp", None, (400, 532)),
    "mudguard-fitted": (SRC / "05-mudguard/2-fitted.webp", (0, 200, 994, 945), (480, 994)),
    "cnc-machine":     (UP / "eadca23c63ffbc190c0a0576d2287183.jpg", (0, 900, 4284, 5712), (480, 960, 1400)),
    "portrait":        (UP / "b88b6f4e55536f13602a9dec436dbf46.jpg", (0, 200, 2021, 3400), (420, 840)),
    "leofly-stand":    (SRC / "06-leofly/3-stand.webp", None, (480, 709)),
    "ambiance-4axis":  (SRC / "07-ambiance/3-4axis.webp", None, (480, 709)),
    "ambiance-rig":    (SRC / "07-ambiance/4-test-rig.webp", None, (480, 709)),
    "ambiance-cfd":    (SRC / "07-ambiance/5-cfd-flow.png", None, (640, 1368)),
}

meta = {}
for name, (src, box, widths) in IMAGES.items():
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if box: im = im.crop(box)
    if name == "crossbow-proto": im = im.resize((490, 841), Image.LANCZOS)   # same framing as the CAD view
    out = []
    for w in widths:
        w = min(w, im.width); h = round(im.height * w / im.width)
        im.resize((w, h), Image.LANCZOS).save(OUT / f"{name}-{w}.webp", "WEBP", quality=78, method=6)
        out.append(w)
    meta[name] = {"w": im.width if len(out) == 1 else max(out), "h": round(im.height * max(out) / im.width), "widths": out}
(OUT / "sizes.json").write_text(json.dumps(meta, indent=1))

# Open Graph image: the section render, 1200 x 630
im = Image.open(SRC / "01-cubesat-accelerometer/2-cad-render-section.webp").convert("RGB")
im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
top = (im.height - 630) // 2 - 40
im.crop((0, top, 1200, top + 630)).save(OUT.parent / "og.jpg", "JPEG", quality=84, optimize=True)
print(len(meta), "images")
