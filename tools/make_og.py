#!/usr/bin/env python3
"""Render assets/img/og-home.jpg (1200x630), the default link-preview image.

    python3 tools/make_og.py

Built from local files only (the logo badge plus brand type), so it never depends on a
remote photo. Re-run after changing the phone number or the strapline in build.py.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build import PHONE, ROOT  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

W, H = 1200, 630
BLACK, GREEN, WHITE, GREY = (10, 10, 10), (106, 192, 62), (255, 255, 255), (178, 184, 176)
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(size, bold=True):
    return ImageFont.truetype(str(FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


img = Image.new("RGB", (W, H), BLACK)

# Soft green glow behind the badge, plus faint mown stripes across the lower half.
glow = Image.new("RGB", (W, H), BLACK)
g = ImageDraw.Draw(glow)
g.ellipse((-120, -80, 620, 700), fill=(28, 52, 20))
glow = glow.filter(ImageFilter.GaussianBlur(140))
img = Image.blend(img, glow, 1.0)
stripes = ImageDraw.Draw(img, "RGBA")
for i, x in enumerate(range(-200, W + 200, 90)):
    if i % 2 == 0:
        stripes.polygon([(x, H), (x + 90, H), (x + 290, 330), (x + 200, 330)], fill=(106, 192, 62, 9))

# Logo badge on the left.
logo = Image.open(ROOT / "assets/img/logo.png").convert("RGBA")
logo = logo.resize((430, 430), Image.LANCZOS)
img.paste(logo, (80, (H - 430) // 2), logo)

d = ImageDraw.Draw(img)
x = 570
# Headline sized to fit the right column with a 60px margin.
size = 66
while d.textlength("LAWN MOWING &", font=font(size)) > W - 60 - x:
    size -= 2
d.text((x, 152), "LAWN MOWING &", font=font(size), fill=WHITE)
d.text((x, 152 + size + 10), "GARDEN CARE", font=font(size), fill=GREEN)
y = 152 + 2 * size + 36
d.rectangle((x, y, x + 72, y + 5), fill=GREEN)
d.text((x, y + 28), "Central Coast and Upper North Shore", font=font(31, bold=False), fill=GREY)
d.text((x, y + 74), "Mowing, hedges, garden beds, clean ups, new turf", font=font(24, bold=False), fill=GREY)
d.text((x, y + 150), "Free quotes", font=font(26), fill=WHITE)
d.text((x + d.textlength("Free quotes", font=font(26)) + 14, y + 150), PHONE, font=font(26), fill=GREEN)

out = ROOT / "assets/img/og-home.jpg"
img.save(out, quality=86, optimize=True)
print("wrote", out, out.stat().st_size // 1024, "KB")
