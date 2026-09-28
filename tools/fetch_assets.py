#!/usr/bin/env python3
"""Download the Higgsfield-generated imagery into assets/img/ as optimised WebP.

    pip install pillow
    python3 tools/fetch_assets.py
    # then set USE_LOCAL_IMAGES = True in build.py and run python3 build.py

Run this from any machine with normal internet access (the build container used
to create the site could not reach the Higgsfield CDN).
"""
import io, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build import IMAGES, ROOT, GBP_PHOTOS  # noqa: E402
from PIL import Image  # noqa: E402

OUT = ROOT / "assets" / "img"
WIDE = {"hero": 1600, "macro": 1400, "about-ute": 1400, "area-north-shore": 1400, "area-central-coast": 1400, "contact-dusk": 1400}
for name, url in IMAGES.items():
    print("fetching", name)
    data = urllib.request.urlopen(url, timeout=120).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    maxw = WIDE.get(name, 1200)
    im.thumbnail((maxw, maxw))
    im.save(OUT / f"{name}.webp", format="WEBP", quality=78, method=6)
    if name == "hero":
        im.resize((1200, int(1200 * im.height / im.width))).crop((0, 0, 1200, 630)).save(OUT / "og-home.jpg", quality=82)
print("done. Now set USE_LOCAL_IMAGES = True in build.py and run: python3 build.py")

# Real job photos from Google Drive (public folder). Kept portrait as-is, max 1000px tall.
WORK = OUT / "work"; WORK.mkdir(exist_ok=True)
for p in GBP_PHOTOS:
    print("fetching work photo", p["n"])
    data = urllib.request.urlopen(f"https://drive.google.com/uc?export=download&id={p['id']}", timeout=120).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((1000, 1000))
    im.save(WORK / f"photo-{p['n']}.webp", format="WEBP", quality=80, method=6)
