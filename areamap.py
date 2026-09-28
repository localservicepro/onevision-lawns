"""Stylised, self-contained SVG map of the two service regions.

Coordinates are approximate suburb centroids (lat, lon) plotted with a simple
equirectangular projection. Good to ~1 km, which is all a schematic map needs.
"""
import math

UNS_XY = {
 "Roseville":(-33.78,151.18),"Lindfield":(-33.775,151.17),"East Lindfield":(-33.77,151.19),"Killara":(-33.765,151.16),
 "East Killara":(-33.76,151.18),"Gordon":(-33.755,151.155),"Pymble":(-33.745,151.14),"West Pymble":(-33.76,151.13),
 "Turramurra":(-33.733,151.13),"South Turramurra":(-33.745,151.11),"North Turramurra":(-33.71,151.15),"Warrawee":(-33.725,151.12),
 "Wahroonga":(-33.717,151.115),"North Wahroonga":(-33.70,151.12),"St Ives":(-33.73,151.16),"St Ives Chase":(-33.70,151.17),
 "Hornsby":(-33.70,151.10),"Normanhurst":(-33.72,151.10),"Waitara":(-33.71,151.10),"Thornleigh":(-33.73,151.08),
 "Westleigh":(-33.72,151.07),"Asquith":(-33.685,151.11),"Hornsby Heights":(-33.67,151.10),"Mount Colah":(-33.67,151.12),
 "Mount Ku-ring-gai":(-33.65,151.14),
}
CC_XY = {
 "Woy Woy":(-33.485,151.32),"Blackwall":(-33.50,151.33),"Booker Bay":(-33.51,151.34),"Ettalong Beach":(-33.51,151.33),
 "Umina Beach":(-33.52,151.31),"Patonga":(-33.55,151.27),"Pearl Beach":(-33.55,151.30),"Killcare":(-33.52,151.36),
 "Killcare Heights":(-33.52,151.37),"Hardys Bay":(-33.52,151.36),"Pretty Beach":(-33.52,151.35),"Wagstaffe":(-33.525,151.34),
 "Empire Bay":(-33.495,151.36),"Daleys Point":(-33.50,151.36),"Horsfield Bay":(-33.49,151.30),"Gosford":(-33.425,151.34),
 "West Gosford":(-33.43,151.32),"East Gosford":(-33.44,151.35),"North Gosford":(-33.41,151.34),"Point Clare":(-33.44,151.33),
 "Tascott":(-33.45,151.32),"Koolewong":(-33.47,151.32),"Wyoming":(-33.40,151.36),"Springfield":(-33.42,151.37),
 "Narara":(-33.39,151.35),"Niagara Park":(-33.38,151.35),"Lisarow":(-33.37,151.37),"Fountaindale":(-33.36,151.40),
 "Somersby":(-33.36,151.29),"Kariong":(-33.44,151.29),"Picketts Valley":(-33.45,151.40),"Matcham":(-33.42,151.41),
 "Holgate":(-33.41,151.41),"Erina":(-33.435,151.39),"Erina Heights":(-33.43,151.41),"Green Point":(-33.46,151.37),
 "Terrigal":(-33.45,151.44),"North Avoca":(-33.455,151.43),"Avoca Beach":(-33.465,151.43),"Copacabana":(-33.49,151.43),
 "Macmasters Beach":(-33.50,151.42),"Forresters Beach":(-33.41,151.47),"Wamberal":(-33.43,151.45),"Bateau Bay":(-33.39,151.48),
 "Killarney Vale":(-33.38,151.47),"Long Jetty":(-33.36,151.48),"The Entrance":(-33.34,151.50),"The Entrance North":(-33.33,151.50),
 "Blue Bay":(-33.36,151.50),"Toowoon Bay":(-33.36,151.50),"Shelly Beach":(-33.37,151.49),"Chittaway Bay":(-33.33,151.44),
 "Chittaway Point":(-33.32,151.45),"Tuggerah":(-33.31,151.42),"Wyong":(-33.28,151.42),"Wyongah":(-33.28,151.47),
 "Tacoma":(-33.28,151.44),"Tacoma South":(-33.29,151.45),"Mardi":(-33.28,151.40),"Alison":(-33.27,151.42),
 "Jilliby":(-33.24,151.39),"Woongarrah":(-33.24,151.47),"Kanwal":(-33.26,151.48),"Hamlyn Terrace":(-33.25,151.48),
 "Wadalba":(-33.26,151.46),"Warnervale":(-33.23,151.45),"Berkeley Vale":(-33.35,151.43),"Glenning Valley":(-33.36,151.44),
 "Ourimbah":(-33.35,151.37),"Palm Grove":(-33.32,151.35),"Toukley":(-33.27,151.54),"Norah Head":(-33.28,151.57),
 "Noraville":(-33.27,151.55),"Canton Beach":(-33.27,151.55),"Budgewoi":(-33.23,151.55),"Buff Point":(-33.24,151.53),
 "San Remo":(-33.22,151.52),"Blue Haven":(-33.21,151.50),"Charmhaven":(-33.23,151.49),"Lake Haven":(-33.24,151.50),
 "Gorokan":(-33.26,151.52),"Mannering Park":(-33.16,151.54),"Summerland Point":(-33.13,151.57),"Gwandalan":(-33.14,151.59),
 "Chain Valley Bay":(-33.17,151.60),"Mooney Mooney":(-33.53,151.20),"Little Wobby":(-33.545,151.25),"Spencer":(-33.46,151.15),
 "Lower Mangrove":(-33.41,151.16),"Central Mangrove":(-33.31,151.23),"Mangrove Mountain":(-33.31,151.13),
}
COAST = [(-33.86,151.29),(-33.80,151.30),(-33.75,151.31),(-33.70,151.31),(-33.66,151.325),(-33.62,151.335),(-33.58,151.335),
 (-33.575,151.32),(-33.58,151.30),(-33.57,151.26),(-33.55,151.23),(-33.535,151.215),(-33.52,151.225),(-33.545,151.25),(-33.555,151.27),
 (-33.55,151.30),(-33.53,151.31),(-33.515,151.325),(-33.51,151.335),(-33.50,151.33),(-33.49,151.32),(-33.47,151.32),(-33.45,151.32),
 (-33.43,151.33),(-33.42,151.34),(-33.44,151.355),(-33.46,151.37),(-33.475,151.375),(-33.49,151.365),(-33.50,151.355),(-33.515,151.345),
 (-33.525,151.34),(-33.53,151.35),(-33.52,151.37),(-33.50,151.41),(-33.49,151.43),(-33.465,151.435),(-33.445,151.445),(-33.42,151.46),
 (-33.40,151.48),(-33.38,151.49),(-33.36,151.50),(-33.34,151.505),(-33.31,151.53),(-33.28,151.58),(-33.25,151.575),(-33.22,151.58),
 (-33.18,151.60),(-33.15,151.63),(-33.10,151.65),(-33.06,151.66)]
LAKES = [
 [(-33.30,151.45),(-33.29,151.49),(-33.31,151.52),(-33.34,151.50),(-33.36,151.48),(-33.35,151.45),(-33.33,151.44)],
 [(-33.24,151.53),(-33.23,151.56),(-33.26,151.57),(-33.28,151.55),(-33.27,151.52)],
 [(-33.18,151.55),(-33.17,151.59),(-33.21,151.60),(-33.22,151.57),(-33.20,151.54)],
 [(-33.06,151.52),(-33.06,151.62),(-33.12,151.61),(-33.15,151.58),(-33.16,151.55),(-33.13,151.53)],
 [(-33.58,151.30),(-33.60,151.29),(-33.65,151.30),(-33.66,151.31),(-33.62,151.315),(-33.59,151.315)],
]
RIVER = [(-33.55,151.23),(-33.53,151.20),(-33.50,151.17),(-33.47,151.15),(-33.43,151.15),(-33.40,151.16),(-33.36,151.18)]
M1 = [(-33.717,151.115),(-33.70,151.10),(-33.65,151.14),(-33.60,151.17),(-33.53,151.20),(-33.48,151.25),(-33.44,151.29),(-33.425,151.34),
 (-33.35,151.37),(-33.31,151.42),(-33.28,151.42),(-33.23,151.45),(-33.20,151.52),(-33.16,151.55),(-33.14,151.59)]
LABELS = ["Hornsby","St Ives","Roseville","Gosford","Woy Woy","Terrigal","The Entrance","Wyong","Toukley","Gwandalan","Mangrove Mountain"]

LAT_TOP, LAT_BOT, LON_L, LON_R = -33.06, -33.84, 150.96, 151.78
W, H = 700, 1000
def proj(lat, lon):
    x = (lon - LON_L) / (LON_R - LON_L) * W
    y = (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * H
    return round(x, 1), round(y, 1)
def path(pts, close=False):
    d = "M" + " L".join(f"{x},{y}" for x, y in (proj(a, b) for a, b in pts))
    return d + (" Z" if close else "")

def area_map(focus=None):
    coast = path(COAST)
    ocean = coast + f" L{W},{H} L{W},0 Z"
    lakes = "".join(f'<path class="am-water" d="{path(l, True)}"/>' for l in LAKES)
    river = f'<path class="am-river" d="{path(RIVER)}"/>'
    m1 = path(M1)
    def dots(d, cls):
        out = ""
        for i, (name, (la, lo)) in enumerate(d.items()):
            x, y = proj(la, lo)
            out += f'<g class="am-dot {cls}" data-suburb="{name}" style="--i:{i}"><circle cx="{x}" cy="{y}" r="9" class="am-halo"/><circle cx="{x}" cy="{y}" r="3.2"/><title>{name}</title></g>'
        return out
    labels = ""
    for name in LABELS:
        la, lo = (UNS_XY.get(name) or CC_XY.get(name))
        x, y = proj(la, lo)
        anchor = "end" if name in ("Hornsby","Woy Woy") else "start"
        dx = -10 if anchor == "end" else 10
        labels += f'<text class="am-label" x="{x+dx}" y="{y+4}" text-anchor="{anchor}">{name}</text>'
    def hull_glow(d):
        xs = [proj(a, b) for a, b in d.values()]
        cx = sum(x for x, _ in xs) / len(xs); cy = sum(y for _, y in xs) / len(xs)
        rx = max(abs(x - cx) for x, _ in xs) + 40; ry = max(abs(y - cy) for _, y in xs) + 40
        return f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}"/>'
    cls = f" am-focus-{focus}" if focus else ""
    return f'''<div class="area-map{cls}" aria-hidden="true">
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
  <defs>
    <radialGradient id="am-glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#6ac03e" stop-opacity=".22"/><stop offset="1" stop-color="#6ac03e" stop-opacity="0"/></radialGradient>
    <pattern id="am-grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M50 0H0V50" fill="none" stroke="rgba(255,255,255,.035)" stroke-width="1"/></pattern>
  </defs>
  <rect width="{W}" height="{H}" class="am-land"/>
  <rect width="{W}" height="{H}" fill="url(#am-grid)"/>
  <path class="am-water am-ocean" d="{ocean}"/>
  {lakes}{river}
  <path class="am-coast" d="{coast}"/>
  <g class="am-region am-region-uns" fill="url(#am-glow)">{hull_glow(UNS_XY)}</g>
  <g class="am-region am-region-cc" fill="url(#am-glow)">{hull_glow(CC_XY)}</g>
  <path class="am-m1" d="{m1}"/>
  <g class="am-dots-uns">{dots(UNS_XY, "am-uns")}</g>
  <g class="am-dots-cc">{dots(CC_XY, "am-cc")}</g>
  {labels}
  <g class="am-ute"><circle r="7" class="am-ute-ring"/><circle r="4"/><animateMotion dur="14s" repeatCount="indefinite" path="{m1}" rotate="auto" keyPoints="0;1;1;0;0" keyTimes="0;.45;.5;.95;1" calcMode="linear"/></g>
  <text class="am-compass" x="{W-40}" y="60" text-anchor="middle">N</text><path class="am-compass-arrow" d="M{W-40},22 l6,14 h-12 z"/>
  <text class="am-sea" x="{W-110}" y="{H-60}" text-anchor="middle">TASMAN SEA</text>
</svg>
<div class="am-tip" role="status"></div>
</div>'''
