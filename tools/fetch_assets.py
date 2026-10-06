#!/usr/bin/env python3
"""Download the site imagery into assets/img/ as optimised WebP: the client's own job photos
(from Google Drive, which must stay shared "anyone with the link") plus the Higgsfield-generated images.

    pip install pillow
    python3 tools/fetch_assets.py
    # then set USE_LOCAL_IMAGES = True in build.py and run python3 build.py

Run this from any machine with normal internet access (the build container used
to create the site could not reach the Higgsfield CDN).
"""
import io, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build import IMAGES, DRIVE_PHOTOS, ROOT, drive_url  # noqa: E402
from PIL import Image  # noqa: E402

OUT = ROOT / "assets" / "img"
WIDE = {"hero": 1600, "macro": 1400, "about-ute": 1400, "area-north-shore": 1400, "area-central-coast": 1400, "contact-dusk": 1400}
# Client photos win over a generated image with the same name.
SOURCES = {name: url for name, url in IMAGES.items() if name not in DRIVE_PHOTOS}
SOURCES.update({name: drive_url(name, 1600) for name in DRIVE_PHOTOS})
for name, url in SOURCES.items():
    print("fetching", name)
    data = urllib.request.urlopen(url, timeout=120).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if name in DRIVE_PHOTOS:
        # Portrait phone photos fill wide banners, so keep them 1600px wide.
        if im.width > 1600:
            im = im.resize((1600, round(1600 * im.height / im.width)), Image.LANCZOS)
    else:
        maxw = WIDE.get(name, 1200)
        im.thumbnail((maxw, maxw))
    im.save(OUT / f"{name}.webp", format="WEBP", quality=78, method=6)
    if name == "hero":
        im.resize((1200, int(1200 * im.height / im.width))).crop((0, 0, 1200, 630)).save(OUT / "og-home.jpg", quality=82)
print("done. Now set USE_LOCAL_IMAGES = True in build.py and run: python3 build.py")
