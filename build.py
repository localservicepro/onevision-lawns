#!/usr/bin/env python3
"""
Static site generator for ONEVISION LAWNS & GARDENS.

    python3 build.py

Every page's SEO strings (title / meta / H1 / target keyword) come from the
Step 1 research report and are implemented verbatim. Edit copy in this file,
re-run, commit the generated HTML.
"""
import json, os, re, html as htmlmod
from pathlib import Path
from areamap import area_map

ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Business config
# ---------------------------------------------------------------------------
BUSINESS = "ONEVISION LAWNS & GARDENS"
OWNER = "Lachlan Donohoe"
PHONE = "0408 595 570"
PHONE_RAW = "+61408595570"
EMAIL = "onevisionlawnsgardens@gmail.com"
ADDRESS = {"street": "45 Braeside Road", "suburb": "Greystanes", "state": "NSW", "postcode": "2145"}
GMB = "https://share.google/zm2cHQuHjUxuBLEnU"
FACEBOOK = "https://www.facebook.com/share/1J6kHBYudL/?mibextid=wwXIfr"
# TODO: replace with the real .com.au domain once registered (drives canonical, og:url, sitemap).
SITE_URL = "https://onevisionlawnsandgardens.com.au"
GHL_TRACKING_ID = "tk_98eb122384f74f4bbfd3a2e2026b2166"
# Generated imagery (Higgsfield, gpt_image_2_5). This build environment cannot download from
# the Higgsfield CDN, so pages reference these URLs directly. Run `python3 tools/fetch_assets.py`
# on any normal machine to pull them into assets/img/ as optimised WebP, then set
# USE_LOCAL_IMAGES = True and rebuild. See README.md.
USE_LOCAL_IMAGES = False
_CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3EWpoiN6nlg900Jz4gzZzRlxgtK/"
IMAGES = {
    "hero": _CDN + "hf_20260928_144356_1bd9a75c-f048-459f-a9c2-4f6274e7baf2.png",
    "macro": _CDN + "hf_20260928_144357_84cd974d-70ad-4425-8ac6-8e32f00e3a71.png",
    "lawn-mowing": _CDN + "hf_20260928_144355_48eaa9f2-6737-482e-9cc8-8aa73c52c1cc.png",
    "garden-maintenance": _CDN + "hf_20260928_144356_5835ca1b-c5ec-43e7-829f-09ef76366720.png",
    "turf-installation": _CDN + "hf_20260928_144355_cf7aa6b2-9868-4485-ba0a-bb8b520ec1a3.png",
    "hedge-trimming": _CDN + "hf_20260928_144355_ba751536-dea3-4f9a-ab0c-947d6220cf82.png",
    "clean-ups": _CDN + "hf_20260928_144355_a2a998f3-c0d6-4bab-9fa2-d4a18b380848.png",
    "weed-control": _CDN + "hf_20260928_144354_161304c8-0b17-4e88-b030-3e0f9f165fc8.png",
    "about-ute": _CDN + "hf_20260928_144357_ef100111-bd40-42da-b6ec-6280853718fc.png",
    "area-north-shore": _CDN + "hf_20260928_144355_fdb3b968-2c1f-4823-bc9f-33504b155a73.png",
    "area-central-coast": _CDN + "hf_20260928_144359_8a1100bd-ce3c-44fa-b8e6-3c9a95d0cab4.png",
    "contact-dusk": _CDN + "hf_20260928_144358_8f4a555a-dc15-47e0-9d01-ca31f47c0544.png",
}
# Real job photos supplied by the client (Google Drive folder "Photos for website",
# 1hRLLVRxDJ5nDpxJM0l63fMKK2f9EDR7_). Each one replaces the generated image in its own
# service's existing slots, so layouts are unchanged. Served through Drive's public thumbnail
# endpoint (it converts the iPhone HEIC originals to JPEG) until tools/fetch_assets.py
# self-hosts them. "focus" is the object-position used for every crop of that photo.
DRIVE_PHOTOS = {
    "lawn-mowing":        {"id": "13ePN5JPW4yyHB3ozjJMVmy_qLGSuPQRZ", "focus": "50% 55%"},   # striped backyard lawn
    "garden-maintenance": {"id": "12gkg4P6e-YnNzzOVnTomRF4Ae7d6go77", "focus": "50% 55%"},   # flowering beds by a path
    "turf-installation":  {"id": "1MlLI7ycPTbPZbSAue09IFlQwKdJu5fER", "focus": "40% 28%"},   # new turf on the verge, work ute
    "hedge-trimming":     {"id": "17cWwHclEp2gnpY3S6o-KLIyIHqEcjy5-", "focus": "60% 45%"},   # cone topiary hedges
    "clean-ups":          {"id": "127z9SQy2pulsRn4ZZQHkozlAb-mZFVf8", "focus": "50% 30%"},   # tidied stepping-stone path
    "weed-control":       {"id": "1LZ54gsWrEFjCWQFw_HUM7DiZb4oeZhc4", "focus": "50% 22%"},   # weed-free mulched bed
    "work-lawn-pool":     {"id": "1c5KrYLvhkemH3e5ID0Vd2Y-PaTYXB_ME", "focus": "50% 48%"},   # mown lawn beside a pool
    "work-lawn-steps":    {"id": "1mcrMjrW5nhEXRnImVC36ef9LARS_l5JI", "focus": "50% 40%"},   # stepping stones set in lawn
}

def drive_url(key, w):
    return f"https://drive.google.com/thumbnail?id={DRIVE_PHOTOS[key]['id']}&sz=w{w}"

# Hero loop rendered with Higgsfield (kling3_0, 5s, 16:9). Hot-linked for now; download and self-host at /assets/video/hero.mp4 before launch.
HERO_VIDEO_URL = "https://d8j0ntlcm91z4.cloudfront.net/user_3EWpoiN6nlg900Jz4gzZzRlxgtK/hf_20260928_145907_35c8138b-ebb4-4b24-a53b-6f0c2e2602be.mp4"
CTA = "Get a Free Quote"

UNS = ["Roseville","Lindfield","East Lindfield","Killara","East Killara","Gordon","Pymble","West Pymble","Turramurra","South Turramurra","North Turramurra","Warrawee","Wahroonga","North Wahroonga","St Ives","St Ives Chase","Hornsby","Normanhurst","Waitara","Thornleigh","Westleigh","Asquith","Hornsby Heights","Mount Colah","Mount Ku-ring-gai"]
CC = ["Woy Woy","Blackwall","Booker Bay","Ettalong Beach","Umina Beach","Patonga","Pearl Beach","Killcare","Killcare Heights","Hardys Bay","Pretty Beach","Wagstaffe","Empire Bay","Daleys Point","Horsfield Bay","Gosford","West Gosford","East Gosford","North Gosford","Point Clare","Tascott","Koolewong","Wyoming","Springfield","Narara","Niagara Park","Lisarow","Fountaindale","Somersby","Kariong","Picketts Valley","Matcham","Holgate","Erina","Erina Heights","Green Point","Terrigal","North Avoca","Avoca Beach","Copacabana","Macmasters Beach","Forresters Beach","Wamberal","Bateau Bay","Killarney Vale","Long Jetty","The Entrance","The Entrance North","Blue Bay","Toowoon Bay","Shelly Beach","Chittaway Bay","Chittaway Point","Tuggerah","Wyong","Wyongah","Tacoma","Tacoma South","Mardi","Alison","Jilliby","Woongarrah","Kanwal","Hamlyn Terrace","Wadalba","Warnervale","Berkeley Vale","Glenning Valley","Ourimbah","Palm Grove","Toukley","Norah Head","Noraville","Canton Beach","Budgewoi","Buff Point","San Remo","Blue Haven","Charmhaven","Lake Haven","Gorokan","Mannering Park","Summerland Point","Gwandalan","Chain Valley Bay","Mooney Mooney","Little Wobby","Spencer","Lower Mangrove","Central Mangrove","Mangrove Mountain"]
assert len(UNS) == 25 and len(CC) == 91

# ---------------------------------------------------------------------------
# Icons (inline SVG, 24x24 stroked)
# ---------------------------------------------------------------------------
ICONS = {
 "grid": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/></svg>',
 "mower": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 15h9l2-6h4"/><circle cx="6" cy="18" r="2.5"/><circle cx="17" cy="18" r="2.5"/><path d="M8.5 18h6M12 15v3M20 9l1-4"/><path d="M4 12c1-2 2-3 3-3"/></svg>',
 "leaf": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19c0-8 5-13 14-14 0 9-4 14-12 14"/><path d="M5 19c3-4 6-7 10-9"/></svg>',
 "turf": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 18h12"/><path d="M15 18a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/><path d="M15 14h.01"/><path d="M3 18v-2c0-1 1-2 2-2h6"/><path d="M4 9l1-2M7 9l1-2M10 9l1-2"/></svg>',
 "broom": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3l7 7"/><path d="M11 6l7 7-6 6-7-7z"/><path d="M4 20l3-3"/><path d="M8 16l1.5 1.5"/></svg>',
 "shears": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M7.5 16 15 4M16.5 16 9 4"/></svg>',
 "spray": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 9h8l-1 12H9z"/><path d="M10 9V6a2 2 0 0 1 2-2h1"/><path d="M15 4h4"/><path d="M19 4l2-2M19 4l2 2"/></svg>',
 "phone": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>',
 "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
 "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 "check": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7"/></svg>',
 "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 "star": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5l2.9 6.2 6.8.8-5 4.7 1.3 6.8L12 17.7 6 21l1.3-6.8-5-4.7 6.8-.8z"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/><path d="m9 12 2 2 4-4"/></svg>',
 "calendar": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
 "user": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
 "map": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 6 6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/></svg>',
 "fb": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.4c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.3H7.4V14h2.8v8z"/></svg>',
 "google": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.6 12.2c0-.7-.1-1.3-.2-1.9H12v3.6h5.4c-.2 1.2-.9 2.3-2 3v2.5h3.2c1.9-1.7 3-4.3 3-7.2z"/><path d="M12 22c2.7 0 5-.9 6.6-2.4l-3.2-2.5c-.9.6-2 1-3.4 1-2.6 0-4.8-1.8-5.6-4.1H3.1v2.6C4.8 19.8 8.1 22 12 22z"/><path d="M6.4 14c-.2-.6-.3-1.3-.3-2s.1-1.4.3-2V7.4H3.1C2.4 8.8 2 10.4 2 12s.4 3.2 1.1 4.6z"/><path d="M12 5.9c1.5 0 2.8.5 3.8 1.5l2.9-2.9C17 2.9 14.7 2 12 2 8.1 2 4.8 4.2 3.1 7.4l3.3 2.6c.8-2.3 3-4.1 5.6-4.1z"/></svg>',
}

# ---------------------------------------------------------------------------
# Services (from the Phase 4 spec: H1, meta title, target keyword, audience)
# ---------------------------------------------------------------------------
SERVICES = [
 {"slug":"lawn-maintenance","name":"Lawn Maintenance","short":"Lawn Mowing","icon":"mower","img":"lawn-mowing.webp",
  "dd":"Hornsby & the Upper North Shore","card":"Regular mowing, edging and lawn care for Hornsby, Wahroonga, Turramurra and the Central Coast. Fortnightly or as needed.",
  "kw":"lawn mowing hornsby",
  "h1":"Lawn Mowing Hornsby & the Upper North Shore",
  "title":"Lawn Mowing Hornsby & Upper North Shore | ONEVISION LAWNS",
  "meta":"Lawn mowing Hornsby and the Upper North Shore. Regular mowing, edging and lawn care from Roseville to Mount Ku-ring-gai. Free quotes from ONEVISION LAWNS.",
  "audience":"Homeowners, landlords and strata"},
 {"slug":"garden-maintenance","name":"Garden Maintenance","short":"Garden Care","icon":"leaf","img":"garden-maintenance.webp",
  "dd":"Central Coast & North Shore","card":"Pruning, weeding, mulching and bed care on a regular schedule, so the garden stays tidy without you lifting a finger.",
  "kw":"garden maintenance central coast",
  "h1":"Garden Maintenance Central Coast: Regular Gardeners You Can Book",
  "title":"Garden Maintenance Central Coast | Gardeners | ONEVISION",
  "meta":"Garden maintenance Central Coast. Regular gardeners for pruning, weeding, mulching and bed care from Woy Woy to Wyong. Book a free quote with ONEVISION.",
  "audience":"Busy households, retirees and holiday-home owners"},
 {"slug":"turf-installation","name":"Turf Installation","short":"New Turf","icon":"turf","img":"turf-installation.webp",
  "dd":"Gosford, Terrigal, Erina & beyond","card":"Old lawn out, ground prepared, new turf laid and rolled. Buffalo, couch and kikuyu suited to coastal and North Shore blocks.",
  "kw":"turf laying central coast",
  "h1":"Turf Laying Central Coast: Professional Turf Installation",
  "title":"Turf Laying Central Coast NSW | ONEVISION LAWNS & GARDENS",
  "meta":"Turf laying Central Coast NSW. Site preparation, soil, levelling and new turf in Gosford, Terrigal, Erina and Wyong. Free quotes from ONEVISION.",
  "audience":"New builds, renovators and lawn replacements"},
 {"slug":"hedge-trimming","name":"Hedge Trimming","short":"Hedges","icon":"shears","img":"hedge-trimming.webp",
  "dd":"Wahroonga, St Ives & the North Shore","card":"Straight tops, clean faces and shaped feature hedges, with every clipping cleared away before we leave.",
  "kw":"hedge trimming north shore",
  "h1":"Hedge Trimming North Shore: Neat Hedges for Upper North Shore Homes",
  "title":"Hedge Trimming North Shore | ONEVISION LAWNS & GARDENS",
  "meta":"Hedge trimming North Shore. Neat, shaped hedges for Upper North Shore homes in Wahroonga, St Ives, Turramurra and Pymble. Free quotes from ONEVISION.",
  "audience":"Established-garden homeowners"},
 {"slug":"garden-clean-ups","name":"Clean Ups","short":"Garden Clean Ups","icon":"broom","img":"clean-ups.webp",
  "dd":"Pre-sale, end of lease & overgrown yards","card":"One-off garden clean ups that bring an overgrown yard back to tidy in a day, with all green waste removed.",
  "kw":"garden clean up central coast",
  "h1":"Garden Clean Up Central Coast: Overgrown Yards Brought Back",
  "title":"Garden Clean Up Central Coast | ONEVISION LAWNS & GARDENS",
  "meta":"Garden clean up Central Coast. One-off clean ups for overgrown yards, pre-sale tidies and end of lease from Woy Woy to Wyong. Free quotes from ONEVISION.",
  "audience":"Pre-sale, end of lease and neglected yards"},
 {"slug":"weed-control","name":"Weed Control","short":"Weed Control","icon":"spray","img":"weed-control.webp",
  "dd":"Lawns, garden beds & paths","card":"Targeted weed treatment for lawns, garden beds, driveways and paths, followed up so the weeds stay gone.",
  "kw":"weed control central coast",
  "h1":"Weed Control Central Coast for Lawns, Garden Beds & Paths",
  "title":"Weed Control Central Coast | ONEVISION LAWNS & GARDENS",
  "meta":"Weed control Central Coast for lawns, garden beds, driveways and paths. Targeted treatment and follow-up from Gosford to The Entrance. Free quotes.",
  "audience":"Homeowners with lawn weeds, driveways and paths"},
]
SVC_BY = {s["slug"]: s for s in SERVICES}

def svc_url(slug): return f"/services/{slug}/"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def esc(s): return htmlmod.escape(s, quote=True)

def chips(items, link=None):
    return '<ul class="chips">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"

def local_business(extra=None):
    lb = {
      "@type": ["LocalBusiness", "LandscapeArchitect"],  # closest schema.org types; "Gardener" is not a schema.org type
      "@id": SITE_URL + "/#business",
      "name": BUSINESS,
      "url": SITE_URL + "/",
      "telephone": PHONE_RAW,
      "email": EMAIL,
      "image": SITE_URL + "/assets/img/logo.jpg",
      "logo": SITE_URL + "/assets/img/logo.jpg",
      "priceRange": "$$",
      "founder": {"@type": "Person", "name": OWNER},
      "address": {"@type": "PostalAddress", "streetAddress": ADDRESS["street"], "addressLocality": ADDRESS["suburb"], "addressRegion": ADDRESS["state"], "postalCode": ADDRESS["postcode"], "addressCountry": "AU"},
      "areaServed": [
        {"@type": "AdministrativeArea", "name": "Central Coast NSW"},
        {"@type": "AdministrativeArea", "name": "Upper North Shore, Sydney NSW"},
        {"@type": "AdministrativeArea", "name": "Hornsby Shire NSW"},
      ] + [{"@type": "Place", "name": f"{s} NSW"} for s in UNS + CC],
      "sameAs": [FACEBOOK, GMB],
      "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], "opens": "06:00", "closes": "18:00"}],
      "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Lawn and garden services", "itemListElement": [
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": SITE_URL + svc_url(s["slug"])}} for s in SERVICES]},
    }
    if extra: lb.update(extra)
    return lb

def breadcrumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u} for i, (n, u) in enumerate(items)]}

def faq_schema(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faqs]}

def crumbs_html(items):
    out = '<ol class="crumbs">'
    for i, (n, u) in enumerate(items):
        out += f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{esc(n)}</li>'
    return out + "</ol>"

# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------
def head(title, meta, path, og_img="/assets/img/og-home.jpg", schema=None, noindex=False):
    canonical = SITE_URL + path
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    graph = {"@context": "https://schema.org", "@graph": schema or []}
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta)}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(BUSINESS)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(meta)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}{og_img}">
<meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(meta)}">
<meta name="twitter:image" content="{SITE_URL}{og_img}">
<meta name="theme-color" content="#0a0a0a">
<script>document.documentElement.classList.add("js")</script>
<meta name="geo.region" content="AU-NSW">
<link rel="icon" href="/assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/logo-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css">
{jsonld(graph)}
<!-- GoHighLevel form / conversion tracking -->
<script src="https://link.msgsndr.com/js/external-tracking.js" data-tracking-id="{GHL_TRACKING_ID}"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

def header_html(active="", solid=False):
    dd_items = f"""<a class="dd-item" role="menuitem" href="/services/"><span class="dd-icon">{ICONS['grid']}</span><span class="dd-text"><strong>All Services</strong><em>Complete lawn &amp; garden upkeep</em></span></a>"""
    for s in SERVICES:
        dd_items += f"""<a class="dd-item" role="menuitem" href="{svc_url(s['slug'])}"><span class="dd-icon">{ICONS[s['icon']]}</span><span class="dd-text"><strong>{esc(s['name'])}</strong><em>{esc(s['dd'])}</em></span></a>"""
    def nl(href, label, key):
        cls = "nav-link is-active" if key == active else "nav-link"
        return f'<a href="{href}" class="{cls}">{label}</a>'
    m_items = '<a href="/services/">All Services</a>' + "".join(f'<a href="{svc_url(s["slug"])}">{esc(s["name"])}</a>' for s in SERVICES)
    cls = "site-header solid" if solid else "site-header"
    return f"""<header class="{cls}" id="top">
  <div class="nav-inner">
    <a href="/" class="brand" aria-label="{esc(BUSINESS)} home"><img src="/assets/img/logo.png" width="56" height="56" alt="{esc(BUSINESS)} logo"><span>ONEVISION<small>LAWNS &amp; GARDENS</small></span></a>
    <nav class="nav-main" aria-label="Main navigation">
      {nl('/', 'Home', 'home')}
      <div class="nav-dropdown">
        <button class="nav-link nav-trigger{' is-active' if active=='services' else ''}" aria-expanded="false" aria-controls="services-menu" aria-haspopup="true">Services <svg class="caret" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>
        <div class="dropdown-panel" id="services-menu" role="menu">{dd_items}</div>
      </div>
      {nl('/about/', 'About', 'about')}
      {nl('/areas/', 'Areas', 'areas')}
      {nl('/blog/', 'Blog', 'blog')}
      {nl('/contact/', 'Contact', 'contact')}
    </nav>
    <div class="nav-actions">
      <a href="tel:{PHONE_RAW}" class="nav-phone" aria-label="Call {PHONE}">{ICONS['phone']}<span class="ph-txt">{PHONE}</span></a>
      <a href="/contact/#quote" class="btn btn--primary">{CTA}</a>
    </div>
    <button class="nav-burger" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav"><span></span><span></span><span></span></button>
  </div>
</header>
<nav class="mobile-nav" id="mobile-nav" aria-label="Mobile navigation">
  <a href="/">Home</a>
  <button class="m-acc" aria-expanded="false">Services <svg class="caret" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>
  <div class="m-acc-panel">{m_items}</div>
  <a href="/about/">About</a>
  <a href="/areas/">Areas</a>
  <a href="/blog/">Blog</a>
  <a href="/contact/">Contact</a>
  <div class="m-cta">
    <a href="tel:{PHONE_RAW}" class="btn btn--ghost">{ICONS['phone']} Call {PHONE}</a>
    <a href="/contact/#quote" class="btn btn--primary">{CTA}</a>
  </div>
</nav>
<main id="main">
"""

def footer_html():
    svc_links = "".join(f'<li><a href="{svc_url(s["slug"])}">{esc(s["name"])}</a></li>' for s in SERVICES)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="/assets/img/logo.png" width="92" height="92" alt="{esc(BUSINESS)} logo" loading="lazy">
        <p>Lawn mowing, garden maintenance, hedges, clean ups, weed control and new turf for homes across the Central Coast and Sydney's Upper North Shore.</p>
        <div class="nap">
          <a href="tel:{PHONE_RAW}">{PHONE}</a>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <span>{ADDRESS['street']}, {ADDRESS['suburb']} {ADDRESS['state']} {ADDRESS['postcode']}</span>
          <span>Mon to Sat, from 6am</span>
        </div>
        <div class="footer-social">
          <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="ONEVISION on Facebook">{ICONS['fb']}</a>
          <a href="{GMB}" target="_blank" rel="noopener" aria-label="ONEVISION on Google">{ICONS['google']}</a>
        </div>
      </div>
      <div>
        <h4>Services</h4>
        <ul><li><a href="/services/">All services</a></li>{svc_links}</ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="/about/">About ONEVISION</a></li>
          <li><a href="/areas/">Areas we service</a></li>
          <li><a href="/areas/upper-north-shore/">Upper North Shore</a></li>
          <li><a href="/blog/">Lawn &amp; garden blog</a></li>
          <li><a href="/contact/">Contact &amp; free quote</a></li>
        </ul>
      </div>
      <div>
        <h4>Get a free quote</h4>
        <ul>
          <li>Send us your address, a rough size and what you need done. We come back with a price, not a sales pitch.</li>
          <li><a href="/contact/#quote" class="btn btn--primary" style="margin-top:10px">{CTA}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-suburbs">
      <b>Upper North Shore:</b> {", ".join(UNS)}.<br>
      <b>Central Coast:</b> {", ".join(CC)}.
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-year>2026</span> {esc(BUSINESS)}. ABN on request.</span>
      <span><a href="/privacy/">Privacy</a> &middot; <a href="/sitemap.xml">Sitemap</a> &middot; Site by <a href="https://localservicepro.com.au" rel="noopener" target="_blank">Local Service Pro</a></span>
    </div>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""

def quote_form(form_id, preselect=None, compact=False, heading="Get your free quote", hint="Tell us what needs doing and we will come back with a price, usually the same day."):
    opts = '<option value="" disabled selected>Select a service</option>'
    for s in SERVICES:
        sel = " selected" if preselect == s["slug"] else ""
        opts += f'<option value="{esc(s["name"])}"{sel}>{esc(s["name"])}</option>'
    opts += '<option value="Multiple services">Multiple services</option><option value="Not sure yet">Not sure yet</option>'
    if preselect: opts = opts.replace(' disabled selected', ' disabled')
    sizes = "".join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in ["Small (under 300m²)", "Medium (300–600m²)", "Large (600–1000m²)", "Acreage / over 1000m²", "Not sure"])
    return f"""<h3 id="{form_id}-title">{esc(heading)}</h3>
<p class="hint">{esc(hint)}</p>
<form class="quote-form" id="{form_id}" method="post" action="/thank-you/" data-redirect="/thank-you/" novalidate aria-labelledby="{form_id}-title" data-form-name="Free Quote Request">
  <div class="field"><label for="{form_id}-name">Name</label><input id="{form_id}-name" name="full_name" type="text" autocomplete="name" required placeholder="Your name"></div>
  <div class="field"><label for="{form_id}-phone">Phone</label><input id="{form_id}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required placeholder="04xx xxx xxx"></div>
  <div class="field full"><label for="{form_id}-email">Email</label><input id="{form_id}-email" name="email" type="email" autocomplete="email" required placeholder="you@example.com"></div>
  <div class="field full"><label for="{form_id}-address">Property address</label><input id="{form_id}-address" name="property_address" type="text" autocomplete="street-address" required placeholder="Street, suburb"></div>
  <div class="field"><label for="{form_id}-size">Property size</label><select id="{form_id}-size" name="property_size" required><option value="" disabled selected>Select size</option>{sizes}</select></div>
  <div class="field"><label for="{form_id}-service">Service needed</label><select id="{form_id}-service" name="service_needed" required>{opts}</select></div>
  <div class="field full"><label for="{form_id}-notes">Job notes</label><textarea id="{form_id}-notes" name="job_notes" placeholder="Anything we should know: access, pets, how overgrown it is, when you need it done"></textarea></div>
  <div class="hp" hidden aria-hidden="true"><label for="{form_id}-trap">Leave this empty</label><input type="text" id="{form_id}-trap" name="ov_trap" tabindex="-1" autocomplete="off" data-lpignore="true" data-1p-ignore data-form-type="other"></div>
  <button type="submit" class="btn btn--primary btn--block full"><span class="btn-label">{ICONS['arrow']} Send my quote request</span><span class="btn-sending" aria-hidden="true"><span class="spinner"></span> Sending…</span></button>
  <p class="form-status" role="status" aria-live="polite"></p>
  <p class="form-note">No obligation. We reply by phone or email, and never share your details.</p>
</form>"""

def faq_html(faqs, eyebrow="Questions", title="Straight answers before you book", intro=None, light=False, schema_only=False):
    items = ""
    for i, (q, a) in enumerate(faqs):
        items += f"""<div class="faq-item reveal" data-d="{min(i,5)}"><button type="button" aria-expanded="false" aria-controls="faq-{i}"><span>{esc(q)}</span><span class="plus" aria-hidden="true"></span></button><div class="answer" id="faq-{i}"><p>{a}</p></div></div>"""
    cls = "section on-grey" if light else "section on-dark-2 grain"
    return f"""<section class="{cls}" id="faq">
  <div class="wrap faq">
    <div class="reveal">
      <span class="eyebrow">{esc(eyebrow)}</span>
      <h2>{esc(title)}</h2>
      <p>{intro or 'If your question is not here, call ' + PHONE + ' and ask. You will get a straight answer from the person who does the work.'}</p>
      <a href="/contact/#quote" class="btn btn--primary" style="margin-top:8px">{CTA}</a>
    </div>
    <div class="faq__list">{items}</div>
  </div>
</section>"""

def cta_strip(title="Ready for a lawn you do not have to think about?", sub="Free quotes across the Central Coast and Upper North Shore. One call, one number."):
    return f"""<section class="cta-strip">
  <span class="ghost" aria-hidden="true">GO</span>
  <div class="wrap">
    <div><h2>{esc(title)}</h2><p>{esc(sub)}</p></div>
    <div class="actions"><a href="tel:{PHONE_RAW}" class="btn btn--dark">{ICONS['phone']} {PHONE}</a><a href="/contact/#quote" class="btn btn--ghost">{CTA}</a></div>
  </div>
</section>"""

def suburb_list(items):
    return '<ul class="suburbs">' + "".join(f'<li data-suburb-ref="{esc(i)}">{esc(i)}</li>' for i in items) + "</ul>"

def region_card(region, title, count, blurb, anchors, items, link, link_text, d=0, open_list=False):
    return f"""<div class="region-card reveal" data-region="{region}" data-d="{d}">
  <div class="region-head"><h3>{title}</h3><span class="count">{count} suburbs</span></div>
  <p>{blurb}</p>
  <ul class="anchors">{"".join(f"<li>{esc(a)}</li>" for a in anchors)}</ul>
  <details{" open" if open_list else ""}><summary>Every suburb we cover in this region</summary>{suburb_list(items)}</details>
  <a href="{link}" class="link-arrow">{link_text} {ICONS['arrow']}</a>
</div>"""

def areas_block(light=True, heading="Areas we service", eyebrow="Two regions, 116 suburbs", focus=None, intro=None):
    cls = "section on-grey" if light else "section on-dark"
    legend = '<div class="am-legend"><button type="button" data-region="uns">Upper North Shore</button><button type="button" data-region="cc">Central Coast</button></div>'
    m = area_map(focus).replace('<div class="am-tip"', legend + '<div class="am-tip"')
    m = m.replace('<div class="area-map', f'<div class="area-map" data-default-focus="{focus or ""}" data-x="', 1).replace('" data-x="', '', 1) if False else m
    if focus: m = m.replace('aria-hidden="true">', f'aria-hidden="true" data-default-focus="{focus}">', 1)
    return f"""<section class="{cls}" id="areas">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">{esc(eyebrow)}</span>
      <h2>{esc(heading)}</h2>
      <p>{intro or "ONEVISION works two regions: Sydney's Upper North Shore and Hornsby, and the Central Coast from the Peninsula up to Lake Macquarie's southern edge. Hover a suburb to find it on the map."}</p>
    </div>
    <div class="areas-layout">
      <div class="reveal">{m}</div>
      <div class="region-list">
        {region_card("uns", "Upper North Shore &amp; Hornsby", len(UNS), "Big established gardens, tall hedges and shaded lawns from Roseville to Mount Ku-ring-gai.", ["Hornsby","Wahroonga","Turramurra","St Ives","Pymble","Killara"], UNS, "/areas/upper-north-shore/", "Upper North Shore gardener", 1, open_list=(focus=="uns"))}
        {region_card("cc", "Central Coast", len(CC), "Lawn mowing Central Coast homes and holiday houses from Woy Woy and Umina to Gosford, Terrigal, The Entrance, Wyong and Toukley, on coastal lawns and sandy soils.", ["Gosford","Terrigal","Erina","The Entrance","Wyong","Woy Woy","Toukley"], CC, "/areas/", "Every suburb we cover", 2, open_list=(focus=="cc"))}
      </div>
    </div>
  </div>
</section>"""

def page_hero(h1, lede, crumbs, img, alt, eyebrow=None):
    eb = f'<span class="eyebrow fadeup">{eyebrow}</span>' if eyebrow else ""
    return f"""<section class="page-hero">
  <div class="hero__media" data-parallax="0.18"><img src="/assets/img/{img}" alt="{esc(alt)}" width="1600" height="900" fetchpriority="high"></div>
  <div class="hero__scrim"></div>
  <div class="wrap">
    <div class="fadeup">{crumbs_html(crumbs)}</div>
    {eb}
    <h1 class="fadeup" data-d="1">{h1}</h1>
    <p class="lede fadeup" data-d="2">{lede}</p>
    <div class="hero__cta fadeup" data-d="3"><a href="#quote" class="btn btn--primary">{CTA} {ICONS['arrow']}</a><a href="tel:{PHONE_RAW}" class="hero__phone">{ICONS['phone']}{PHONE}</a></div>
  </div>
</section>"""

def service_aside(current=None):
    links = ""
    for s in SERVICES:
        cls = ' class="is-active"' if s["slug"] == current else ""
        links += f'<li><a href="{svc_url(s["slug"])}"{cls}>{esc(s["name"])} {ICONS["arrow"]}</a></li>'
    return f"""<aside class="aside">
  <div class="aside-card">
    <h3>Free, no-pressure quote</h3>
    <p>Send the address and a rough idea of the job. We price it and get back to you, usually the same day.</p>
    <a href="#quote" class="btn btn--primary">{CTA}</a>
    <a href="tel:{PHONE_RAW}" class="hero__phone">{ICONS['phone']}{PHONE}</a>
  </div>
  <div class="aside-card aside-card--light">
    <h3>All services</h3>
    <ul class="aside-list">{links}</ul>
  </div>
</aside>"""

def contact_section(preselect=None, dark=True):
    cls = "section on-dark grain" if dark else "section on-grey"
    return f"""<section class="{cls}" id="contact">
  <div class="wrap contact">
    <div class="reveal">
      <span class="eyebrow">Free quote</span>
      <h2>Tell us about the job</h2>
      <p>Call, email or use the form. Every quote is free, and you deal with {OWNER.split()[0]} directly, not a call centre.</p>
      <div class="contact__info">
        <div class="info-row"><span class="icon">{ICONS['phone']}</span><div><b>Call or text</b><a href="tel:{PHONE_RAW}">{PHONE}</a><small>Mon to Sat, from 6am</small></div></div>
        <div class="info-row"><span class="icon">{ICONS['mail']}</span><div><b>Email</b><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
        <div class="info-row"><span class="icon">{ICONS['map']}</span><div><b>Service areas</b><p>Central Coast and Sydney's Upper North Shore</p><small>Registered office: {ADDRESS['street']}, {ADDRESS['suburb']} {ADDRESS['state']} {ADDRESS['postcode']}</small></div></div>
        <div class="info-row"><span class="icon">{ICONS['star']}</span><div><b>Google</b><a href="{GMB}" target="_blank" rel="noopener">5.0 rated on Google. Read our reviews</a></div></div>
      </div>
    </div>
    <div class="form-card reveal" data-d="1" id="quote">{quote_form('quote-form', preselect)}</div>
  </div>
</section>"""

# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
HOME_FAQ = [
 ("How much does lawn mowing cost on the Central Coast?",
  "Lawn mowing on the Central Coast is priced on the size and condition of the lawn, how often it is cut and whether edges, whipper snipping and green waste removal are included. We quote every lawn individually and confirm the price before we start, so there are no surprises. Regular fortnightly customers pay less per visit than one-off cuts. Send us the address for a free quote."),
 ("Do you offer regular garden maintenance in Hornsby, Wahroonga and Turramurra?",
  "Yes. Regular garden maintenance across Hornsby, Wahroonga, Turramurra and the rest of the Upper North Shore is a core part of what we do. Most customers book fortnightly or monthly visits that cover mowing, edging, pruning, weeding and hedge upkeep, with green waste taken away. You choose the schedule and we keep it."),
 ("Can you lay new turf in Gosford, Terrigal and Erina?",
  "Yes. We install new turf across Gosford, Terrigal, Erina and the wider Central Coast. That includes removing the old lawn, preparing and levelling the soil, laying and rolling the turf, and advising on watering so it establishes properly. We recommend varieties suited to coastal conditions, such as buffalo and couch."),
 ("How often should hedges be trimmed on the Upper North Shore?",
  "Most Upper North Shore hedges need trimming two to three times a year. Fast growers like murraya, lilly pilly and photinia do best with a trim in late spring and again in late summer, with a lighter tidy in autumn. Formal box and conifer hedges hold their shape with less. We can schedule it so you never have to think about it."),
 ("Do you do one-off garden clean ups on the Central Coast before a sale or end of lease?",
  "Yes. One-off garden clean ups are one of our most requested Central Coast jobs. We cut back overgrowth, mow and edge the lawn, weed and tidy the beds, clear paths and take away all green waste, so the property presents well for photos, inspections or a final bond check. Most clean ups are done in a single visit."),
 ("Which suburbs do you cover across the Central Coast and Upper North Shore?",
  "We cover 91 Central Coast suburbs, from Woy Woy, Umina and Ettalong on the Peninsula through Gosford, Erina, Terrigal, The Entrance, Wyong and Toukley to Gwandalan and Mangrove Mountain. On the Upper North Shore we cover 25 suburbs from Roseville, Lindfield and Killara through Pymble, Turramurra, Wahroonga and St Ives to Hornsby, Asquith and Mount Ku-ring-gai."),
]

def build_home():
    title = "Lawn Mowing Central Coast & North Shore | ONEVISION LAWNS"
    meta = "Lawn mowing Central Coast and Upper North Shore. ONEVISION LAWNS & GARDENS handles mowing, garden care, hedges and new turf. Call for a free quote today."
    schema = [local_business(), {"@type": "WebSite", "@id": SITE_URL + "/#website", "url": SITE_URL + "/", "name": BUSINESS, "publisher": {"@id": SITE_URL + "/#business"}},
              {"@type": "WebPage", "@id": SITE_URL + "/#webpage", "url": SITE_URL + "/", "name": title, "isPartOf": {"@id": SITE_URL + "/#website"}, "about": {"@id": SITE_URL + "/#business"}},
              faq_schema(HOME_FAQ), breadcrumbs([("Home", "/")])]
    svc_cards = ""
    for i, s in enumerate(SERVICES):
        svc_cards += f"""<a href="{svc_url(s['slug'])}" class="svc-card reveal" data-d="{i%3}">
  <div class="svc-card__media"><img src="/assets/img/{s['img']}" alt="{esc(s['name'])} on the Central Coast and Upper North Shore by ONEVISION LAWNS &amp; GARDENS" loading="lazy" width="800" height="600"><span class="svc-card__num">0{i+1}</span></div>
  <div class="svc-card__body"><span class="icon">{ICONS[s['icon']]}</span><h3>{esc(s['name'])}</h3><p>{esc(s['card'])}</p><span class="link-arrow">{esc(s['dd'])} {ICONS['arrow']}</span></div>
</a>"""
    marquee = "".join(f"<span>{esc(x)}</span>" for x in ["Lawn mowing", "Garden maintenance", "Turf installation", "Hedge trimming", "Garden clean ups", "Weed control", "Central Coast", "Upper North Shore", "Hornsby", "Gosford", "Terrigal", "Wahroonga", "St Ives", "Wyong", "Woy Woy", "Turramurra"])
    body = header_html("home") + f"""
<section class="hero">
  <div class="hero__media" data-parallax="0.25">
    <video autoplay muted loop playsinline preload="metadata" poster="/assets/img/hero.webp" aria-hidden="true">
      <source src="{HERO_VIDEO_URL}" type="video/mp4">
    </video>
    <img src="/assets/img/hero.webp" alt="Freshly mown striped lawn in front of a Central Coast home, cut by ONEVISION LAWNS &amp; GARDENS" width="1600" height="900" fetchpriority="high" style="position:absolute;inset:0;z-index:-1">
  </div>
  <div class="hero__scrim"></div>
  <div class="wrap hero__grid">
    <div>
      <span class="eyebrow fadeup">Central Coast &middot; Upper North Shore</span>
      <h1 class="fadeup" data-d="1">Lawn Mowing Central Coast &amp; Upper North Shore, <span class="accent">Done Properly</span></h1>
      <p class="lede fadeup" data-d="2">ONEVISION LAWNS &amp; GARDENS mows, edges, trims, weeds and lays new turf for homes from Woy Woy to Wyong and Roseville to Mount Ku-ring-gai. Free quotes, one number to call, and the same person turning up each time.</p>
      <div class="hero__cta fadeup" data-d="3">
        <a href="#quote-hero" class="btn btn--primary">{CTA} {ICONS['arrow']}</a>
        <a href="tel:{PHONE_RAW}" class="hero__phone">{ICONS['phone']}{PHONE}</a>
      </div>
      <ul class="trust fadeup" data-d="4">
        <li>{ICONS['check']} 5.0 on Google</li>
        <li>{ICONS['check']} Free quotes</li>
        <li>{ICONS['check']} No lock-in</li>
        <li>{ICONS['check']} Owner operated</li>
      </ul>
    </div>
    <div class="hero__card fadeup" data-d="3" id="quote-hero">
      {quote_form('quote-form-hero', heading='Get a free quote', hint='Takes a minute. We reply the same day.')}
    </div>
  </div>
  <div class="scroll-cue" aria-hidden="true"></div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee__track">{marquee}{marquee}</div></div>

<section class="section on-light" id="about-intro">
  <div class="wrap intro">
    <div class="reveal">
      <span class="eyebrow">Lawn &amp; garden care, two regions</span>
      <h2>Reliable lawn mowing on the Central Coast, and proper garden care on the North Shore</h2>
      <p class="lede">ONEVISION LAWNS &amp; GARDENS is an owner-operated lawn mowing and garden maintenance business working the Central Coast and Sydney's Upper North Shore. Lawn mowing Central Coast customers get the same thing Hornsby and Wahroonga customers get: a tidy, edged lawn on a schedule you set, and a garden that gets looked after instead of just cut.</p>
      <p>Whether it is a fortnightly mow in Terrigal, a hedge in Pymble, a pre-sale clean up in Umina Beach or a new lawn in Gosford, you deal with {OWNER.split()[0]} directly. Both regions get the same crew and the same standard. No call centre, no franchise fees built into the price, and no chasing anyone to find out when they are coming.</p>
      <ul class="checks">
        <li>{ICONS['check']} Mowing, edging and whipper snipping every visit, with clippings taken away</li>
        <li>{ICONS['check']} Fortnightly, monthly or one-off. You set the schedule and we keep it</li>
        <li>{ICONS['check']} Quoted up front, priced on your lawn, not a template</li>
      </ul>
      <a href="/about/" class="link-arrow" style="margin-top:26px">More about ONEVISION {ICONS['arrow']}</a>
    </div>
    <div class="intro__media reveal" data-d="1">
      <img src="/assets/img/work-lawn-pool.webp" alt="Healthy mown backyard lawn beside a fenced pool, looked after by ONEVISION LAWNS &amp; GARDENS" loading="lazy" width="1200" height="900">
      <div class="intro__badge"><b>5.0</b>Google rating</div>
    </div>
  </div>
</section>

<section class="section on-dark grain" id="services">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">What we do</span>
      <h2>Six services, one crew, both regions</h2>
      <p>Lawn mowing Central Coast and North Shore homes rely on is the core of it, with garden care, hedges, clean ups, weed control and new turf around it. Every service has its own page with what is included and where we do it.</p>
    </div>
    <div class="services-grid">{svc_cards}</div>
  </div>
</section>

<section class="section on-grey" id="why">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Why ONEVISION</span>
      <h2>What a lawn mowing service on the Central Coast should actually be</h2>
      <p>Two of the three businesses in the Central Coast map results do not even have a website. Plenty more will not answer the phone. Here is the standard we hold ourselves to instead.</p>
    </div>
    <div class="tiles">
      <div class="tile reveal"><span class="icon">{ICONS['user']}</span><h3>Same person, every time</h3><p>Owner operated. The person who quotes the job is the person who does it, and who answers the phone afterwards.</p></div>
      <div class="tile reveal" data-d="1"><span class="icon">{ICONS['calendar']}</span><h3>Turns up when booked</h3><p>Fortnightly, monthly or one-off. We keep a schedule and tell you if weather moves it, rather than leaving you to guess.</p></div>
      <div class="tile reveal" data-d="2"><span class="icon">{ICONS['broom']}</span><h3>Finished means finished</h3><p>Edges done, paths blown off, clippings and green waste gone. You should not know we were there except for the lawn.</p></div>
      <div class="tile reveal" data-d="3"><span class="icon">{ICONS['shield']}</span><h3>Priced on your yard</h3><p>Free quote on the actual lawn and garden, not a franchise rate card. Regular customers pay less per visit.</p></div>
    </div>
  </div>
</section>

<section class="band">
  <img src="/assets/img/macro.webp" alt="Close-up of freshly cut grass blades with morning dew" loading="lazy" data-parallax="-0.15">
  <div class="band__inner"><p class="reveal">Cut properly. Edged properly. <span class="accent">Every fortnight.</span></p></div>
</section>

<section class="section on-dark-2" id="process">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">How it works</span>
      <h2>From first call to first cut in three steps</h2>
    </div>
    <div class="steps">
      <div class="step reveal"><h3>Send the address</h3><p>Call {PHONE} or fill in the form with your address, a rough lawn size and what you need. Photos help but are not essential.</p></div>
      <div class="step reveal" data-d="1"><h3>Get a fixed price</h3><p>We price the job from what you send, or drop by if it is a bigger clean up or a turf job. You get a number before anything starts.</p></div>
      <div class="step reveal" data-d="2"><h3>We turn up and do it</h3><p>Lawn mowed and edged, hedges trimmed, beds weeded, waste gone. Regulars go on a schedule and stay there.</p></div>
    </div>
  </div>
</section>

{areas_block(light=True)}

<section class="section on-dark grain" id="reviews">
  <div class="wrap proof">
    <div class="score reveal">
      <div>
        <div class="big">5.0</div>
        <div class="stars" aria-label="Five stars">{ICONS['star']*5}</div>
        <p>Rated 5.0 on Google by lawn mowing Central Coast and Upper North Shore customers.</p>
      </div>
      <a href="{GMB}" target="_blank" rel="noopener" class="btn btn--dark">Read our Google reviews {ICONS['arrow']}</a>
    </div>
    <div class="proof-card reveal" data-d="1">
      <span class="eyebrow">What customers get</span>
      <h2 style="font-size:1.6rem">The lawn mowing Central Coast homeowners keep rebooking</h2>
      <ul>
        <li>{ICONS['check']} A confirmed price before the first visit, and the same price every visit after</li>
        <li>{ICONS['check']} Mowing, edging, whipper snipping and blow-down included as standard</li>
        <li>{ICONS['check']} Green waste removed, not left in a pile by the bin</li>
        <li>{ICONS['check']} A text the day before so you know we are coming</li>
      </ul>
    </div>
  </div>
</section>

{faq_html(HOME_FAQ, title="Lawn mowing Central Coast questions, answered", light=True)}
{contact_section()}
""" + footer_html()
    write("index.html", head(title, meta, "/", schema=schema) + body)
    return body

# ---------------------------------------------------------------------------
# SERVICE PAGES
# ---------------------------------------------------------------------------
SERVICE_BODIES = {
"lawn-maintenance": {
 "lede": "Regular lawn mowing for Hornsby and the Upper North Shore, from Roseville up to Mount Ku-ring-gai, plus the Central Coast. Mowed, edged, whipper snipped and blown down, on a schedule that suits you.",
 "img": "lawn-mowing.webp", "alt": "Freshly mown backyard lawn with even stripes inside a colorbond fence, maintained by ONEVISION LAWNS & GARDENS",
 "body": f"""
<h2>Lawn mowing in Hornsby that turns up when it says it will</h2>
<p>Lawn mowing Hornsby customers book with ONEVISION for one reason: it gets done, properly, on the day we said. Hornsby and the Upper North Shore have big blocks, shaded lawns under gums and buffalo that grows a foot in a wet fortnight. A quick pass with a mower does not cut it, so ours is a full lawn maintenance visit every time.</p>
<p>Each lawn mowing Hornsby visit includes mowing to the right height for your grass type, edging along paths, driveways and garden beds, whipper snipping around trees, fences and retaining walls, and blowing down hard surfaces so nothing is left behind. Clippings are caught and removed unless you prefer them mulched back in.</p>

<h2>What is included in a lawn mowing Hornsby visit</h2>
<ul>
  <li><strong>Mowing</strong> at the correct height for buffalo, couch, kikuyu or a mixed lawn, with stripes if the lawn allows it</li>
  <li><strong>Edging</strong> of every hard edge: paths, driveways, kerbs, garden beds and pavers</li>
  <li><strong>Whipper snipping</strong> around trees, posts, fences, sheds and retaining walls</li>
  <li><strong>Blow down</strong> of paths, driveway and patio, so the place looks finished, not just cut</li>
  <li><strong>Green waste removed</strong> from the property with us</li>
  <li><strong>Optional add-ons</strong>: fertilising, aerating, top dressing, weed treatment and hedge trimming on the same visit</li>
</ul>

<div class="mini-grid">
  <div class="mini"><b>Fortnightly</b><span>The standard for spring and summer on the North Shore. Lawn never gets away from you.</span></div>
  <div class="mini"><b>Monthly</b><span>Suits winter, shaded lawns and slower growers like buffalo in cooler months.</span></div>
  <div class="mini"><b>One-off</b><span>Overgrown lawn, pre-inspection tidy or a cut while you are away. Priced on condition.</span></div>
</div>

<h2>Where we mow on the Upper North Shore</h2>
<p>Lawn mowing Hornsby is the anchor, but we service every suburb from Roseville to Mount Ku-ring-gai: Lindfield, Killara, Gordon, Pymble, West Pymble, Turramurra, Warrawee, Wahroonga, St Ives, Normanhurst, Waitara, Thornleigh, Westleigh, Asquith, Hornsby Heights and Mount Colah, as well as Hornsby itself. These are established gardens with mature trees, long driveways and formal edges, and we treat them that way.</p>
<p>The same crew also covers the <a href="/">Central Coast</a>, so if you have a holiday home in Terrigal, Avoca or Umina Beach and a family home in Wahroonga, one phone call covers both.</p>

<h2>Lawn mowing Hornsby: how pricing works</h2>
<p>Every lawn is quoted on its own size, access and condition. A tidy 300 square metre lawn on a fortnightly schedule costs less per visit than a one-off cut on a block that has not been touched since autumn. We confirm the price before the first visit and it stays the same for every visit after, unless you change the scope.</p>
<p>Regular lawn mowing Hornsby customers get priority scheduling through the September to March growing season, which is when every mowing service on the North Shore is at capacity. Booking a schedule now is the easiest way to guarantee your spot.</p>

<h2>Lawn mowing Hornsby style: looking after North Shore lawns all year</h2>
<p>Lawns from Hornsby to Killara live under tall gums, which means shade, leaf litter and compacted soil. A good lawn maintenance program adjusts for that: higher cuts in shade, aerating in spring, a feed before the growth flush and weed control before bindii sets seed. Ask about a seasonal plan and we will build one around your lawn rather than a generic calendar.</p>
<p>Need more than mowing? See our <a href="/services/garden-maintenance/">garden maintenance</a>, <a href="/services/hedge-trimming/">hedge trimming</a> and <a href="/services/weed-control/">weed control</a> pages, or <a href="/contact/">get a free quote</a> for the lot.</p>
""",
 "faq": [
  ("How much does lawn mowing cost in Hornsby?", "Lawn mowing in Hornsby is priced on the size of the lawn, how overgrown it is, access and how often you book. Fortnightly regulars pay less per visit than one-off cuts. Send us the address and a rough size and we will quote it, usually the same day, with the price confirmed before we start."),
  ("How often should I have my lawn mowed on the Upper North Shore?", "Fortnightly from September to March, and every three to four weeks through winter. Buffalo lawns in shaded Upper North Shore gardens can stretch further in the cooler months. We adjust the schedule with the season so the lawn is never scalped or left to get away."),
  ("Do you take the grass clippings away?", "Yes. Clippings and any whipper snipping debris are removed from the property at the end of every visit. If you would rather have the clippings mulched back into the lawn as a feed, just say so when you book."),
  ("Do you mow lawns on the Central Coast as well?", "Yes. ONEVISION covers both the Upper North Shore and the Central Coast, from Woy Woy through Gosford and Terrigal to Wyong and Toukley. Lawn mowing across both regions is run on the same schedule system, so a holiday home and a family home can be looked after by the same crew."),
  ("Can you handle strata and rental properties?", "Yes. We look after lawns for landlords, property managers and small strata blocks across Hornsby and the Upper North Shore. We can invoice the agent directly and send a photo when each visit is done."),
 ]},
"garden-maintenance": {
 "lede": "Regular gardeners for the Central Coast, from Woy Woy and Umina to Gosford, Terrigal, The Entrance and Wyong. Pruning, weeding, mulching, hedges and lawns on a schedule, with the green waste gone when we leave.",
 "img": "garden-maintenance.webp", "alt": "Pruned garden beds of flowering shrubs and purple foliage either side of a sandstone path, kept by ONEVISION LAWNS & GARDENS",
 "body": f"""
<h2>Garden maintenance Central Coast homeowners can actually book</h2>
<p>Finding a gardener on the Central Coast who turns up regularly is harder than it should be. ONEVISION offers proper garden maintenance Central Coast wide: a fortnightly or monthly visit that keeps the whole garden in order, not a once-a-year blitz. Beds weeded, shrubs pruned, hedges kept in shape, lawns mowed and edged, and the waste taken away.</p>
<p>The Central Coast is a different gardening environment to Sydney. Sandy soils on the Peninsula, salt wind in Terrigal, Avoca and Wamberal, heavy clay around Wyong and dense bushland gardens in Kariong, Somersby and Mangrove Mountain. We adjust what we do and when we do it to the block in front of us.</p>

<h2>What regular garden maintenance Central Coast visits cover</h2>
<ul>
  <li><strong>Weeding</strong> of garden beds, paths and borders, by hand and with targeted treatment where needed</li>
  <li><strong>Pruning and shaping</strong> of shrubs, natives, roses and small trees at the right time of year</li>
  <li><strong>Hedge trimming</strong> for murraya, lilly pilly, viburnum, photinia and formal box</li>
  <li><strong>Mulching</strong> to hold moisture through Central Coast summers and keep weeds down</li>
  <li><strong>Lawn mowing and edging</strong> on the same visit, so one booking covers the whole yard</li>
  <li><strong>Seasonal tasks</strong>: fertilising, deadheading, cutting back perennials, clearing leaf litter and gutters at ground level</li>
  <li><strong>Green waste removal</strong> every visit</li>
</ul>

<h2>Who books a regular gardener on the Central Coast</h2>
<div class="mini-grid">
  <div class="mini"><b>Busy households</b><span>Working families in Erina, Lisarow and Warnervale who want the garden done without spending the weekend on it.</span></div>
  <div class="mini"><b>Retirees</b><span>Established gardens in Umina, Ettalong and Bateau Bay that need a steady hand rather than a bulldozer.</span></div>
  <div class="mini"><b>Holiday-home owners</b><span>Properties in Terrigal, Avoca, Killcare and Pearl Beach kept tidy between visits and ready for guests.</span></div>
</div>

<h2>Garden maintenance Central Coast wide</h2>
<p>We cover 91 Central Coast suburbs. On the Peninsula that means Woy Woy, Blackwall, Booker Bay, Ettalong Beach, Umina Beach, Pearl Beach and Patonga. Around Gosford it is West, East and North Gosford, Point Clare, Wyoming, Narara, Niagara Park, Lisarow and Kariong. On the coast, Erina, Terrigal, Avoca Beach, Copacabana, Macmasters Beach, Wamberal, Forresters Beach, Bateau Bay, Long Jetty, The Entrance, Blue Bay, Toowoon Bay and Shelly Beach. North of Tuggerah, we cover Wyong, Berkeley Vale, Ourimbah, Toukley, Norah Head, Budgewoi, Lake Haven, Gorokan, Summerland Point and Gwandalan. The full list is on our <a href="/areas/">areas page</a>.</p>
<p>We also run regular garden maintenance on <a href="/areas/upper-north-shore/">Sydney's Upper North Shore</a>, so if you have properties in both places, one gardener can handle both.</p>

<h2>How a garden maintenance Central Coast schedule works</h2>
<p>The first visit is usually a longer reset to bring the garden back to a baseline: overgrowth cut back, beds cleared and mulched, hedges reshaped. After that, regular visits are shorter and cheaper because we are maintaining rather than rescuing. You get a fixed price per visit, a text the day before, and the same gardener each time.</p>
<p>If the garden has got well away, start with a <a href="/services/garden-clean-ups/">garden clean up</a> and move onto a schedule from there. Weed problems in lawns and paths are handled under <a href="/services/weed-control/">weed control</a>.</p>
""",
 "faq": [
  ("How much does garden maintenance cost on the Central Coast?", "Garden maintenance on the Central Coast is priced per visit based on the size of the garden, how much is planted, how often we come and what the first reset visit involves. Regular fortnightly or monthly customers pay a fixed rate per visit. Send us the address for a free quote and we will confirm the price before we start."),
  ("What is included in a regular gardening visit?", "A standard visit covers weeding, pruning, hedge upkeep, mulching as needed, lawn mowing and edging, and removal of all green waste. Seasonal jobs like fertilising and cutting back perennials are worked in through the year. You can add or remove tasks at any time."),
  ("How often should a Central Coast garden be maintained?", "Most Central Coast gardens do best on a fortnightly visit from September to March and monthly through winter. Coastal gardens with fast-growing hedges and buffalo lawns need the fortnightly rhythm in summer. Low-maintenance native gardens can often stretch to monthly all year."),
  ("Do you look after holiday homes and rentals?", "Yes. A lot of our Central Coast garden maintenance customers own holiday homes in Terrigal, Avoca, Killcare and Pearl Beach, or rentals managed by an agent. We keep the property presentable between guests or tenants, invoice whoever you nominate and can send photos after each visit."),
  ("Is ONEVISION a gardener or a lawn mowing business?", "Both. ONEVISION LAWNS & GARDENS does full garden maintenance as well as lawn mowing, hedge trimming, clean ups, weed control and turf installation. Most regular customers have us do the lawn and the garden on the same visit, which works out cheaper than booking two separate trades."),
 ]},
"turf-installation": {
 "lede": "New lawns laid properly across the Central Coast: old turf removed, soil prepared and levelled, the right variety chosen for your block and rolled in so it takes. Gosford, Terrigal, Erina, Wyong and everywhere between.",
 "img": "turf-installation.webp", "alt": "New turf laid along a front verge and nature strip, with the ONEVISION LAWNS & GARDENS work ute parked alongside",
 "body": f"""
<h2>Turf laying Central Coast blocks need, not a roll-and-run job</h2>
<p>A new lawn fails for one of two reasons: the wrong grass for the site, or poor preparation underneath it. ONEVISION handles turf laying Central Coast wide with both sorted before a single roll goes down. We strip the old lawn, fix the levels, bring in the right soil, lay the turf tight and roll it, then tell you exactly how to water it for the first month.</p>
<p>Sandy Peninsula blocks in Umina and Woy Woy drain too fast, clay around Wyong and Tuggerah drains too slowly, and coastal sites in Terrigal, Avoca and Wamberal cop salt wind. Each needs a different preparation and often a different grass. We have laid lawns on all of them.</p>

<h2>Our turf laying Central Coast process</h2>
<ul>
  <li><strong>Site assessment</strong>: sun, shade, drainage, soil type and how the lawn will be used</li>
  <li><strong>Removal</strong> of the old lawn, weeds and debris, taken off site</li>
  <li><strong>Soil preparation</strong>: rotary hoeing, imported turf underlay where needed, levelling and grading for drainage</li>
  <li><strong>Starter fertiliser</strong> and a final rake before laying</li>
  <li><strong>Laying</strong> in a brickwork pattern with tight joins, cut cleanly around beds, paths and edges</li>
  <li><strong>Rolling and first water</strong>, then a written watering and mowing plan for the establishment period</li>
</ul>

<h2>Which turf suits the Central Coast?</h2>
<div class="mini-grid">
  <div class="mini"><b>Sir Walter / Sapphire buffalo</b><span>The coast's default. Soft leaf, handles part shade and salt, low maintenance once established.</span></div>
  <div class="mini"><b>Couch (Wintergreen, Santa Ana)</b><span>Full sun, fine leaf, takes heavy wear. Good for open backyards in Wyong, Kanwal and Hamlyn Terrace.</span></div>
  <div class="mini"><b>Kikuyu</b><span>Fast, tough and cheap to establish. Best for big sunny blocks and acreage in Somersby, Jilliby and Mangrove Mountain.</span></div>
</div>
<p>We also supply Zoysia for premium low-mow lawns and shade-tolerant blends for gardens under gums. If you are not sure, tell us where the lawn is and how it gets used and we will recommend one.</p>

<h2>When to book turf laying Central Coast wide</h2>
<p>Turf can be laid year round on the Central Coast, but spring (September to November) and early autumn (March to April) give the fastest establishment with the least watering. Summer laying works if you can commit to daily watering for the first two to three weeks. Winter laying is fine for buffalo, just slower to knit. Turf searches on the coast spike every September for a reason: it is the best month to book.</p>

<h2>Turf laying Central Coast: Gosford to Toukley</h2>
<p>We install new lawns across the Central Coast including Gosford, East and West Gosford, Point Clare, Kariong, Erina, Terrigal, Avoca Beach, Wamberal, Bateau Bay, The Entrance, Tuggerah, Wyong, Berkeley Vale, Ourimbah, Warnervale, Toukley and Budgewoi, as well as on Sydney's <a href="/areas/upper-north-shore/">Upper North Shore</a>. New builds, renovations, lawn replacements after a pool or extension, and patch repairs are all quoted free.</p>
<p>Once the lawn is in, our <a href="/services/lawn-maintenance/">lawn maintenance</a> service can take over the first cuts and the ongoing schedule so it establishes properly.</p>
""",
 "faq": [
  ("How much does turf laying cost on the Central Coast?", "Turf installation on the Central Coast is priced per square metre and depends on the variety, how much preparation the site needs, whether old lawn has to be removed and access for soil delivery. We measure the area, recommend a grass and give you a fixed written quote covering supply, preparation and laying."),
  ("What is the best turf for Central Coast conditions?", "Sir Walter or Sapphire buffalo is the safest choice for most Central Coast homes: it copes with part shade, salt wind and sandy or clay soil. Couch suits full-sun lawns that get heavy use. Kikuyu is the budget option for large sunny blocks. We match the grass to the site before quoting."),
  ("How long does new turf take to establish?", "New turf on the Central Coast usually roots in two to three weeks in spring and summer, and four to six weeks in winter. Keep it moist for the first fortnight, avoid walking on it, and give it its first mow once you cannot lift a corner. We provide a watering schedule with every job."),
  ("Do you remove the old lawn first?", "Yes. We strip the old lawn and weeds, take the waste off site, then hoe, level and prepare the soil before laying. Laying new turf over an old lawn is the most common reason a new lawn fails, so we do not do it."),
  ("Can you lay turf in Gosford, Terrigal and Erina?", "Yes. Gosford, Terrigal and Erina are right in the middle of our Central Coast service area, along with 88 other suburbs from Woy Woy to Gwandalan. We can usually inspect within a few days and lay within a week or two of the turf order, depending on the season."),
 ]},
"hedge-trimming": {
 "lede": "Straight tops, clean faces and shaped feature hedges for Upper North Shore homes in Wahroonga, St Ives, Turramurra, Pymble, Killara and Hornsby. Clippings cleared before we leave.",
 "img": "hedge-trimming.webp", "alt": "Cone-shaped topiary hedges freshly trimmed along a sandstone retaining wall, clippings still on the path",
 "body": f"""
<h2>Hedge trimming North Shore gardens were built around</h2>
<p>The Upper North Shore runs on hedges. Murraya along the front fence, lilly pilly screening the neighbours, box edging the beds and the occasional three-metre photinia that nobody has been game to touch in years. ONEVISION does hedge trimming North Shore wide, from Roseville to Mount Ku-ring-gai, with the tools and the eye to get lines straight and faces clean, and every clipping cleared away afterwards.</p>
<p>We trim by hand and with powered hedgers as the job needs, use string lines on long formal runs, and work off platforms and ladders for tall screens. The result is a hedge that looks like a hedge, not something that was hacked at on a Saturday.</p>

<h2>What we trim</h2>
<ul>
  <li><strong>Formal hedges</strong>: murraya, buxus, lilly pilly, viburnum, photinia, escallonia and conifer</li>
  <li><strong>Privacy screens</strong> and tall boundary hedges, up to around four metres from the ground or a platform</li>
  <li><strong>Topiary and feature shapes</strong>: balls, cones and cloud pruning kept crisp</li>
  <li><strong>Reductions</strong>: bringing an overgrown hedge back to a manageable height and width in stages</li>
  <li><strong>Low borders</strong> along paths, beds and driveways</li>
  <li><strong>Clean up and removal</strong> of every clipping, with paths and lawn blown down</li>
</ul>

<h2>How often hedge trimming North Shore hedges need</h2>
<div class="mini-grid">
  <div class="mini"><b>Fast growers</b><span>Murraya, lilly pilly, photinia: late spring, late summer and a light autumn tidy. Two to three times a year.</span></div>
  <div class="mini"><b>Formal box &amp; conifer</b><span>Once or twice a year holds the shape. Never cut conifers back into bare wood.</span></div>
  <div class="mini"><b>Reductions</b><span>Overgrown hedges are brought down in two or three cuts over a season so they recover, not die back.</span></div>
</div>
<p>Most of our hedge customers put trimming on a schedule with their <a href="/services/garden-maintenance/">garden maintenance</a> or <a href="/services/lawn-maintenance/">lawn mowing</a>, so it simply happens at the right time of year without a separate booking.</p>

<h2>Hedge trimming North Shore wide, Roseville to Hornsby</h2>
<p>We trim hedges in Wahroonga, North Wahroonga, St Ives, St Ives Chase, Turramurra, South and North Turramurra, Warrawee, Pymble, West Pymble, Gordon, Killara, East Killara, Lindfield, East Lindfield and Roseville, and through Hornsby Shire in Hornsby, Hornsby Heights, Normanhurst, Waitara, Thornleigh, Westleigh, Asquith, Mount Colah and Mount Ku-ring-gai. Established federation and mid-century gardens with mature hedging are what we see most, and what we are set up for.</p>
<p>The same service runs on the <a href="/">Central Coast</a>, where coastal hedges of westringia, coprosma and lilly pilly need trimming just as often.</p>

<h2>Getting a hedge trimming North Shore quote</h2>
<p>Send a photo of the hedge with something in frame for scale, or the address and a rough length and height. Most hedge jobs can be quoted from photos. Bigger reductions and very tall screens we will look at in person. Either way the price is confirmed before we start, and it includes taking the clippings away.</p>
""",
 "faq": [
  ("How much does hedge trimming cost on the North Shore?", "Hedge trimming on the Upper North Shore is priced on the length, height and type of hedge, how overgrown it is and access. A tidy of an established murraya hedge costs a lot less than a staged reduction of a four-metre photinia screen. Send a photo or the address for a free quote, with clipping removal included."),
  ("How often should hedges be trimmed on the Upper North Shore?", "Two to three times a year for fast growers such as murraya, lilly pilly and photinia: late spring, late summer and a light autumn tidy. Formal box and conifer hedges hold their shape on one or two trims a year. Regular trimming keeps hedges dense and avoids hard reductions later."),
  ("Can you reduce a hedge that has grown too tall?", "Yes, in stages. Most hedges tolerate being brought down by about a third in one cut, so an overgrown screen is reduced over two or three trims across a growing season. Conifers are the exception and cannot be cut back into bare wood, so we manage their height rather than reduce it."),
  ("Do you take the hedge clippings away?", "Yes. Every hedge trimming job includes raking and removing the clippings, and blowing down paths, lawn and driveway afterwards. You are left with a trimmed hedge and a clean yard, nothing else."),
  ("Do you trim hedges on the Central Coast too?", "Yes. ONEVISION trims hedges across the Central Coast as well as the Upper North Shore, from Woy Woy and Umina through Gosford, Terrigal and The Entrance to Wyong and Toukley. Coastal hedges of westringia, coprosma and lilly pilly are trimmed on the same schedule system."),
 ]},
"garden-clean-ups": {
 "lede": "One-off garden clean ups across the Central Coast for overgrown yards, pre-sale presentation and end of lease. Cut back, mowed, weeded, cleared and hauled away, usually in a single visit.",
 "img": "clean-ups.webp", "alt": "Tidied garden path of sandstone stepping stones between trimmed rosemary and clipped round shrubs after a garden clean up",
 "body": f"""
<h2>Garden clean up Central Coast yards that have got away</h2>
<p>Some gardens just need a reset. A rental that has come back overgrown, a house going on the market next week, a block you bought with the garden untouched for years, or a family home where the yard got away over a busy summer. ONEVISION does garden clean up Central Coast wide, and we turn up with the mower, the hedgers, the brushcutter and the trailer to get it done in one go.</p>
<p>We work the whole coast, from Woy Woy, Umina and Ettalong on the Peninsula through Gosford, Erina, Terrigal and The Entrance to Wyong, Toukley and Budgewoi. Most one-off clean ups are finished in a single day, and all the green waste leaves with us.</p>

<h2>What a garden clean up Central Coast job includes</h2>
<ul>
  <li><strong>Overgrown lawn</strong> brushcut, mowed and edged, however long it has got</li>
  <li><strong>Shrubs and hedges</strong> cut back, shaped or removed as needed</li>
  <li><strong>Garden beds</strong> weeded, dead plants pulled, edges redefined and mulched if wanted</li>
  <li><strong>Paths, driveways and patios</strong> cleared of weeds, leaf litter and debris</li>
  <li><strong>Vines and climbers</strong> pulled off fences, sheds and gutters</li>
  <li><strong>Small tree work</strong>: low limbs lifted, dead wood out, suckers removed</li>
  <li><strong>All green waste removed</strong> from the property, no piles left by the bin</li>
</ul>

<h2>Clean ups for every reason</h2>
<div class="mini-grid">
  <div class="mini"><b>Pre-sale</b><span>Agents in Terrigal, Erina and Gosford know a tidy garden photographs better and sells faster. We get the yard ready for the photographer.</span></div>
  <div class="mini"><b>End of lease</b><span>Tenants and property managers across the coast use us to get the garden back to handover condition before the final inspection.</span></div>
  <div class="mini"><b>Neglected yards</b><span>Deceased estates, holiday homes left too long, or a block that simply beat you this year. We have seen worse.</span></div>
</div>

<h2>Spring garden clean up Central Coast bookings</h2>
<p>September is the busiest month of the year for garden clean ups on the Central Coast. Winter growth has thickened, the weeds have set, and everyone wants the yard ready before the warm weather. If you want a spring clean up booked before the rush, contact us in August. Once the reset is done, most customers move onto regular <a href="/services/garden-maintenance/">garden maintenance</a> or <a href="/services/lawn-maintenance/">lawn mowing</a> so it never gets that bad again.</p>

<h2>How a clean up is quoted</h2>
<p>For anything beyond a standard overgrown lawn we will usually look at the property in person or ask for a few photos, because the amount of cutting and the volume of green waste drive the price. You get a fixed price for the whole job before we start, including waste removal. No hourly surprises.</p>
<p>Weeds coming back through paths and lawn after a clean up are handled under <a href="/services/weed-control/">weed control</a>, and a wrecked lawn can be replaced under <a href="/services/turf-installation/">turf installation</a>.</p>
""",
 "faq": [
  ("How much does a garden clean up cost on the Central Coast?", "A garden clean up on the Central Coast is priced on the size of the yard, how overgrown it is and how much green waste has to be removed. A standard overgrown-lawn tidy is a few hours; a full reset of a neglected block is a day with a trailer load or two. We quote the whole job as a fixed price, waste included."),
  ("How long does a garden clean up take?", "Most Central Coast garden clean ups are completed in a single visit. A typical suburban yard takes half a day to a full day depending on how much cutting back and removal is involved. Very large or heavily overgrown blocks can run over two days, and we tell you that in the quote."),
  ("Do you remove all the green waste?", "Yes. Every clean up includes loading and removing all green waste from the property, whether that is grass, hedge clippings, branches or pulled weeds. Nothing is left in a pile for you to deal with or for the council bin to take in instalments."),
  ("Can you do a pre-sale garden tidy before the photographer comes?", "Yes, and it is one of the most common clean ups we do across Gosford, Erina, Terrigal and the Peninsula. Tell us the photography date and we schedule the clean up in the days before it, so the lawn is fresh and the beds are tidy when the photos are taken."),
  ("Do you do end of lease garden clean ups?", "Yes. We bring rental gardens back to handover condition for tenants, landlords and property managers across the Central Coast, including mowing, edging, weeding, cutting back and waste removal. We can invoice the agent and send photos of the finished yard for the inspection file."),
 ]},
"weed-control": {
 "lede": "Targeted weed control for Central Coast lawns, garden beds, driveways and paths. Bindii, clover, nutgrass, oxalis and the rest treated properly and followed up, from Gosford to The Entrance and Woy Woy to Wyong.",
 "img": "weed-control.webp", "alt": "Weed-free garden bed finished with fresh bark mulch behind a brick retaining wall",
 "body": f"""
<h2>Weed control Central Coast lawns and gardens actually need</h2>
<p>Pulling weeds by hand on a Saturday works right up until it does not. Once bindii, clover, nutgrass, oxalis or winter grass have set in a lawn or a bed, they come back every season unless they are treated correctly and at the right time. ONEVISION provides weed control Central Coast wide, using the right product for the weed and the surface, applied by someone who knows what the weed is.</p>
<p>The Central Coast's sandy soils, mild winters and coastal humidity mean weeds barely stop growing. A weed control program timed to the seasons is the difference between a lawn you enjoy and one you spend your weekends fighting.</p>

<h2>Where our weed control Central Coast service treats</h2>
<ul>
  <li><strong>Lawns</strong>: selective broadleaf treatment for bindii, clover, cudweed, dandelion and oxalis, and targeted control of nutgrass, winter grass and paspalum without killing the lawn</li>
  <li><strong>Garden beds</strong>: hand weeding, spot treatment and mulching to stop regrowth</li>
  <li><strong>Driveways, paths and pavers</strong>: full-kill treatment of weeds and moss in cracks and joints</li>
  <li><strong>Gravel, fence lines and hard-to-mow strips</strong>: knockdown and residual control</li>
  <li><strong>Pre-emergent treatment</strong> in late winter to stop summer weeds germinating in the first place</li>
</ul>

<h2>The weeds we see most on the coast</h2>
<div class="mini-grid">
  <div class="mini"><b>Bindii</b><span>Treat in winter before it sets its prickles, usually June to August. Too late and the seeds are already there for next year.</span></div>
  <div class="mini"><b>Nutgrass</b><span>The one that beats everyone. Needs a specific selective product and repeat applications, not a general weed killer.</span></div>
  <div class="mini"><b>Clover &amp; oxalis</b><span>Sign of a hungry or compacted lawn. Treated, then fixed with feeding and aeration so they do not return.</span></div>
</div>

<h2>How our weed control Central Coast program works</h2>
<p>We identify what is growing, choose a product that targets it without harming the lawn or plants around it, apply it in the right conditions, and come back to check. Lawn weeds are usually paired with a feed so the grass thickens and crowds out the next generation. Paths and driveways get a treatment that stops regrowth for months rather than weeks.</p>
<p>Where pets and kids use the lawn, we tell you exactly what was applied and how long to stay off it. Where you would prefer no chemical treatment at all, we can hand weed, mulch and manage through mowing height instead.</p>

<h2>Weed control Central Coast wide: Woy Woy to Wyong</h2>
<p>We treat weeds in lawns, beds and hard surfaces across all 91 Central Coast suburbs we cover, including Gosford, Kariong, Erina, Terrigal, Avoca Beach, Wamberal, Bateau Bay, The Entrance, Tuggerah, Wyong, Ourimbah, Toukley, Budgewoi, Woy Woy, Umina Beach and Ettalong Beach, and on Sydney's <a href="/areas/upper-north-shore/">Upper North Shore</a>. Weed control is often bundled with <a href="/services/lawn-maintenance/">lawn maintenance</a> so the treatment lands at the right point in the mowing cycle.</p>
""",
 "faq": [
  ("How much does weed control cost on the Central Coast?", "Weed control on the Central Coast is priced on the area being treated, the type of weed and whether it is a one-off treatment or a seasonal program. A lawn broadleaf treatment is inexpensive; nutgrass or a full program with pre-emergent costs more but fixes the problem. We quote it free after seeing the lawn or photos."),
  ("When is the best time to treat bindii on the Central Coast?", "June to August. Bindii germinates in autumn and sets its seed prickles in spring, so a selective treatment in winter kills the plant before the prickles form. Treating in October or later is too late for that season; the seeds have already dropped for next year."),
  ("Is your weed treatment safe for pets and children?", "We use registered products applied at label rates and tell you exactly what was used and how long to keep pets and children off the treated area, usually until it has dried. If you would prefer no chemical treatment at all, we offer hand weeding, mulching and mowing-based control instead."),
  ("Can you get rid of nutgrass?", "Yes, with the right approach. Nutgrass does not respond to general weed killers and pulling it spreads the tubers. It needs a specific selective herbicide applied to actively growing plants, repeated over a season. We run that program and pair it with lawn feeding so the grass closes over the gaps."),
  ("Do you treat weeds in driveways and paths as well as lawns?", "Yes. Driveways, paths, pavers, gravel and fence lines get a non-selective treatment that kills existing weeds and moss and slows regrowth for months. Lawns get selective products that target the weeds and leave the grass. Both can be done in the same visit."),
 ]},
}

def build_service(s):
    b = SERVICE_BODIES[s["slug"]]
    path = svc_url(s["slug"])
    schema = [{"@type": "Service", "@id": SITE_URL + path + "#service", "name": s["name"], "serviceType": s["name"], "url": SITE_URL + path,
               "description": s["meta"], "provider": {"@id": SITE_URL + "/#business"},
               "areaServed": [{"@type": "AdministrativeArea", "name": "Central Coast NSW"}, {"@type": "AdministrativeArea", "name": "Upper North Shore, Sydney NSW"}]},
              local_business(), faq_schema(b["faq"]), breadcrumbs([("Home", "/"), ("Services", "/services/"), (s["name"], path)])]
    body = header_html("services") + page_hero(esc(s["h1"]), esc(b["lede"]), [("Home", "/"), ("Services", "/services/"), (s["name"], path)], b["img"], b["alt"], eyebrow=s["name"]) + f"""
<section class="section on-light">
  <div class="wrap layout">
    <article class="prose reveal">{b['body']}</article>
    {service_aside(s['slug'])}
  </div>
</section>
{faq_html(b['faq'], eyebrow=s['name'] + ' FAQs', title='Questions about ' + s['name'].lower(), light=False)}
{areas_block(light=True, heading=s['name'] + ' across both regions', eyebrow='Where we do it')}
{contact_section(preselect=s['slug'])}
""" + footer_html()
    write(f"services/{s['slug']}/index.html", head(s["title"], s["meta"], path, og_img=f"/assets/img/{b['img']}", schema=schema) + body)

def build_services_index():
    title = "Lawn & Garden Services Central Coast & North Shore"
    meta = "Lawn mowing, garden care, turf, hedges, clean ups and weed control across the Central Coast and Upper North Shore. Free quotes from ONEVISION."
    path = "/services/"
    cards = ""
    for i, s in enumerate(SERVICES):
        cards += f"""<a href="{svc_url(s['slug'])}" class="svc-card reveal" data-d="{i%3}">
  <div class="svc-card__media"><img src="/assets/img/{s['img']}" alt="{esc(s['name'])} by ONEVISION LAWNS &amp; GARDENS" loading="lazy" width="800" height="600"><span class="svc-card__num">0{i+1}</span></div>
  <div class="svc-card__body"><span class="icon">{ICONS[s['icon']]}</span><h3>{esc(s['h1'].split(':')[0].replace(' & the Upper North Shore','').replace(' for Lawns, Garden Beds & Paths',''))}</h3><p>{esc(s['card'])}</p><span class="link-arrow">{esc(s['dd'])} {ICONS['arrow']}</span></div>
</a>"""
    schema = [local_business(), breadcrumbs([("Home", "/"), ("Services", path)]),
              {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s["name"], "url": SITE_URL + svc_url(s["slug"])} for i, s in enumerate(SERVICES)]}]
    body = header_html("services") + page_hero("Lawn &amp; garden services for the Central Coast and Upper North Shore", "Six services, all done by the same owner-operated crew. Book one, or bundle the lawn, hedges and beds into a single regular visit.", [("Home", "/"), ("Services", path)], "hero.webp", "Freshly mown lawn on the Central Coast", eyebrow="All services") + f"""
<section class="section on-dark grain">
  <div class="wrap"><div class="services-grid">{cards}</div></div>
</section>
{cta_strip()}
{areas_block(light=True)}
{contact_section()}
""" + footer_html()
    write("services/index.html", head(title, meta, path, schema=schema) + body)

# ---------------------------------------------------------------------------
# AREAS
# ---------------------------------------------------------------------------
UNS_FAQ = [
 ("Do you have a gardener available in Hornsby and Wahroonga?", "Yes. ONEVISION runs regular garden maintenance and lawn mowing rounds through Hornsby, Wahroonga, Turramurra, St Ives, Pymble and the rest of the Upper North Shore. Fortnightly and monthly visits are available, along with one-off clean ups and hedge trimming. Call or send the address for a free quote."),
 ("What does a North Shore gardener charge?", "Gardening on the Upper North Shore is priced per visit on the size of the garden, what is planted and how often we come. Regular customers pay a fixed rate each visit. Because North Shore gardens tend to be large and heavily planted, we quote every property individually after seeing it or photos."),
 ("Which Upper North Shore suburbs do you cover?", "All 25: Roseville, Lindfield, East Lindfield, Killara, East Killara, Gordon, Pymble, West Pymble, Turramurra, South Turramurra, North Turramurra, Warrawee, Wahroonga, North Wahroonga, St Ives, St Ives Chase, Hornsby, Normanhurst, Waitara, Thornleigh, Westleigh, Asquith, Hornsby Heights, Mount Colah and Mount Ku-ring-gai."),
 ("Can you handle large established gardens with mature hedges?", "Yes, that is most of what we do on the North Shore. Big federation and mid-century gardens with tall murraya, lilly pilly and photinia hedges, shaded buffalo lawns under gums, and long formal edges. We bring platforms for tall hedges and adjust mowing heights for shade."),
 ("Do you also mow lawns on the North Shore, or just garden?", "Both, on the same visit. Most Upper North Shore customers have ONEVISION mow and edge the lawn, trim the hedges and tidy the beds in one booking, which works out cheaper than a separate mowing service and gardener."),
]

def build_area_uns():
    title = "Gardener North Shore | Upper North Shore Lawns | ONEVISION"
    meta = "Gardener North Shore: regular lawn and garden care for Upper North Shore homes from Roseville to Hornsby and Mount Ku-ring-gai. Free quotes from ONEVISION."
    path = "/areas/upper-north-shore/"
    h1 = "Gardener North Shore: Lawn &amp; Garden Care for the Upper North Shore"
    schema = [local_business(), faq_schema(UNS_FAQ), breadcrumbs([("Home", "/"), ("Areas", "/areas/"), ("Upper North Shore", path)]),
              {"@type": "WebPage", "url": SITE_URL + path, "name": title, "about": {"@type": "Place", "name": "Upper North Shore, Sydney NSW"}}]
    svc_links = "".join(f'<li><a href="{svc_url(s["slug"])}">{esc(s["name"])} {ICONS["arrow"]}</a></li>' for s in SERVICES)
    body = header_html("areas") + page_hero(h1, "Regular gardening, lawn mowing and hedge trimming for the big established gardens of Roseville, Killara, Pymble, Turramurra, Wahroonga, St Ives and Hornsby.", [("Home", "/"), ("Areas", "/areas/"), ("Upper North Shore", path)], "area-north-shore.webp", "Leafy Upper North Shore street with a federation home and manicured front lawn", eyebrow="Upper North Shore &amp; Hornsby") + f"""
<section class="section on-light">
  <div class="wrap layout">
    <article class="prose reveal">
      <h2>A gardener North Shore homes can rely on</h2>
      <p>Finding a reliable gardener on the North Shore is a familiar problem. The gardens up here are large, mature and heavily planted, and a lot of mowing services will not touch the hedges or the beds. ONEVISION LAWNS &amp; GARDENS is a gardener North Shore homeowners book for the whole property: lawn mowed and edged, hedges kept straight, beds weeded and mulched, and the waste gone at the end of every visit.</p>
      <p>We run regular rounds through the Ku-ring-gai suburbs of Roseville, Lindfield, Killara, Gordon, Pymble, Turramurra, Warrawee, Wahroonga and St Ives, and through Hornsby Shire in Hornsby, Normanhurst, Waitara, Thornleigh, Westleigh, Asquith, Hornsby Heights, Mount Colah and Mount Ku-ring-gai. Every suburb between Roseville and the Hawkesbury is covered.</p>

      <h2>What a gardener North Shore homes need does</h2>
      <ul>
        <li><a href="/services/lawn-maintenance/">Lawn mowing in Hornsby</a> and every suburb south to Roseville, on fortnightly or monthly schedules</li>
        <li><a href="/services/garden-maintenance/">Garden maintenance</a>: pruning, weeding, mulching and seasonal care for established gardens</li>
        <li><a href="/services/hedge-trimming/">Hedge trimming on the North Shore</a>, from low box borders to four-metre privacy screens</li>
        <li><a href="/services/garden-clean-ups/">Garden clean ups</a> for pre-sale, end of lease and gardens that have got away</li>
        <li><a href="/services/weed-control/">Weed control</a> for shaded lawns, sandstone paths and long driveways</li>
        <li><a href="/services/turf-installation/">Turf installation</a> and lawn replacement, including shade-tolerant varieties for gardens under gums</li>
      </ul>

      <h2>Gardener North Shore work in Wahroonga, Turramurra, St Ives and Pymble</h2>
      <p>These suburbs have the largest blocks on the North Shore and the most established plantings: camellias, azaleas, magnolias, tall murraya and lilly pilly hedges, and lawns that spend half the day in shade. A gardener in Wahroonga or Turramurra needs to know when to prune what, how high to cut a shaded buffalo lawn, and how to manage a hedge that has been let go. That is the work we do most.</p>
      <div class="mini-grid">
        <div class="mini"><b>Shaded lawns</b><span>Buffalo under gums is cut higher and less often, aerated in spring and fed before the flush. Scalping it is the fastest way to lose it.</span></div>
        <div class="mini"><b>Big hedges</b><span>Murraya and photinia screens trimmed two to three times a year with string lines and platforms. Reductions done in stages.</span></div>
        <div class="mini"><b>Leaf litter</b><span>Gum, liquidambar and jacaranda drop is cleared from lawns, beds and paths through autumn so the lawn does not smother.</span></div>
      </div>

      <h2>Gardener North Shore coverage: Hornsby, Killara and Lindfield</h2>
      <p>South through Gordon, Killara, East Killara, Lindfield, East Lindfield and Roseville the blocks are a little smaller but the standard is the same: formal edges, sandstone paths, hedged frontages and a lawn that is expected to look right. In Hornsby, Waitara, Normanhurst, Thornleigh and Westleigh we see more family homes with bigger backyards and bush borders, which means more brushcutting and more leaf litter. Up through Asquith, Hornsby Heights, Mount Colah and Mount Ku-ring-gai, gardens back onto national park and need managing with that in mind.</p>

      <h2>How to book a gardener North Shore wide</h2>
      <p>Send the address, a rough description of the garden and what you want done, or call {PHONE}. For regular maintenance we will usually visit once to quote and set the schedule. From then on you get the same gardener, a text the day before each visit and a fixed price per visit. If the garden needs a reset first, we start with a <a href="/services/garden-clean-ups/">clean up</a> and move onto the schedule from there.</p>
      <p>We also service the whole <a href="/areas/">Central Coast</a>, so if you have a weekender in Terrigal, Killcare or Pearl Beach it can be looked after by the same crew.</p>
    </article>
    <aside class="aside">
      <div class="aside-card"><h3>Free quote, any suburb</h3><p>Send the address and what needs doing. We come back with a price, usually the same day.</p><a href="#quote" class="btn btn--primary">{CTA}</a><a href="tel:{PHONE_RAW}" class="hero__phone">{ICONS['phone']}{PHONE}</a></div>
      <div class="aside-card aside-card--light"><h3>Services on the North Shore</h3><ul class="aside-list">{svc_links}</ul></div>
    </aside>
  </div>
</section>
{areas_block(light=True, heading="Upper North Shore & Hornsby suburbs we cover", eyebrow="Every suburb", focus="uns", intro="Hover a suburb to find it on the map. Sydney side of the Hawkesbury is the North Shore run; everything north of it is the Central Coast run.")}
{faq_html(UNS_FAQ, eyebrow="Gardener North Shore FAQs", title="Questions from North Shore homeowners")}
{contact_section()}
""" + footer_html()
    write("areas/upper-north-shore/index.html", head(title, meta, path, og_img="/assets/img/area-north-shore.webp", schema=schema) + body)

def build_areas_index():
    title = "Service Areas | Central Coast & Upper North Shore"
    meta = "Every suburb ONEVISION covers: 91 on the Central Coast from Woy Woy to Gwandalan and 25 on the Upper North Shore from Roseville to Mount Ku-ring-gai."
    path = "/areas/"
    schema = [local_business(), breadcrumbs([("Home", "/"), ("Areas", path)])]
    body = header_html("areas") + page_hero("Areas we service: Central Coast &amp; Upper North Shore", "Two regions, 116 suburbs, one crew. Find your suburb below and get a free quote for lawn mowing, garden maintenance, hedges, clean ups, weed control or new turf.", [("Home", "/"), ("Areas", path)], "area-central-coast.webp", "Coastal Central Coast home with a green front lawn and ocean beyond", eyebrow="Where we work") + f"""
<section class="section on-light">
  <div class="wrap">
    <div class="intro" style="margin-bottom:72px">
      <div class="reveal">
        <span class="eyebrow">Central Coast</span>
        <h2>Lawn mowing and garden care across the Central Coast</h2>
        <p class="lede">The Central Coast is our biggest service region. From the Woy Woy Peninsula to the Gosford valleys, the beaches from Terrigal to The Entrance and up through Wyong, Toukley and the lake suburbs, we run regular lawn mowing and garden maintenance rounds through all 91 suburbs below.</p>
        <p>Coastal lawns deal with sandy soil, salt wind and humidity, and holiday homes need looking after between visits. We plan the schedule around that. See <a href="/services/lawn-maintenance/" class="link-arrow">lawn mowing</a>, <a href="/services/garden-maintenance/" class="link-arrow">garden maintenance</a>, <a href="/services/turf-installation/" class="link-arrow">turf</a> or <a href="/services/garden-clean-ups/" class="link-arrow">clean ups</a>.</p>
      </div>
      <div class="intro__media reveal" data-d="1"><img src="/assets/img/area-central-coast.webp" alt="Central Coast home with a neatly mown lawn, Norfolk pines and the ocean beyond" loading="lazy" width="1200" height="900"><div class="intro__badge"><b>91</b>Central Coast suburbs</div></div>
    </div>
  </div>
</section>
<section class="section on-grey">
  <div class="wrap">
    <div class="intro" style="margin-bottom:72px">
      <div class="intro__media reveal"><img src="/assets/img/area-north-shore.webp" alt="Leafy Upper North Shore street with a federation home and manicured lawn" loading="lazy" width="1200" height="900"><div class="intro__badge"><b>25</b>North Shore suburbs</div></div>
      <div class="reveal" data-d="1">
        <span class="eyebrow">Upper North Shore &amp; Hornsby</span>
        <h2>Gardener and lawn mowing for the Upper North Shore</h2>
        <p class="lede">From Roseville and Lindfield through Pymble, Turramurra and Wahroonga to St Ives, Hornsby and Mount Ku-ring-gai. Big established gardens, tall hedges and shaded lawns are the everyday work here.</p>
        <a href="/areas/upper-north-shore/" class="btn btn--dark">Upper North Shore page {ICONS['arrow']}</a>
      </div>
    </div>
  </div>
</section>
{areas_block(light=False, heading="Find your suburb on the map", eyebrow="116 suburbs", intro="Hover a suburb name to light it up on the map, or tap a region to focus it. Both lists are the full set; if your street is in one of them, we come to you.")}
{cta_strip(title="Not sure if we cover your street?", sub="Call and ask. If it is on the Central Coast or the Upper North Shore, the answer is almost certainly yes.")}
{contact_section()}
""" + footer_html()
    write("areas/index.html", head(title, meta, path, og_img="/assets/img/area-central-coast.webp", schema=schema) + body)

# ---------------------------------------------------------------------------
# ABOUT / CONTACT / THANK YOU / PRIVACY / 404
# ---------------------------------------------------------------------------
def build_about():
    title = "About ONEVISION LAWNS & GARDENS | Owner-Operated Lawn Care"
    meta = "ONEVISION LAWNS & GARDENS is an owner-operated lawn and garden business run by Lachlan Donohoe, serving the Central Coast and Upper North Shore."
    path = "/about/"
    schema = [local_business(), breadcrumbs([("Home", "/"), ("About", path)]), {"@type": "AboutPage", "url": SITE_URL + path, "name": title, "about": {"@id": SITE_URL + "/#business"}}]
    body = header_html("about") + page_hero("About ONEVISION LAWNS &amp; GARDENS", f"An owner-operated lawn and garden business run by {OWNER}. One crew, two regions, and a simple promise: turn up when booked, do the whole job, leave the place clean.", [("Home", "/"), ("About", path)], "work-lawn-steps.webp", "Charcoal stepping stones set into a neatly edged lawn, finished by ONEVISION LAWNS & GARDENS", eyebrow="Who we are") + f"""
<section class="section on-light">
  <div class="wrap intro">
    <div class="reveal">
      <span class="eyebrow">The short version</span>
      <h2>One vision: lawns and gardens looked after properly</h2>
      <p class="lede">ONEVISION LAWNS &amp; GARDENS was started by {OWNER} to do lawn and garden maintenance the way customers keep saying they cannot find: reliable, thorough and priced honestly.</p>
      <p>We are not a franchise. There is no territory fee built into your price and no call centre between you and the person doing the work. When you call {PHONE}, you get {OWNER.split()[0]}. When the crew turns up, it is the same crew every visit, and they know your yard.</p>
      <p>We work two regions: the Central Coast, from the Woy Woy Peninsula to Gwandalan, and Sydney's Upper North Shore and Hornsby Shire. The two are different jobs. Coastal lawns, sandy soil and holiday homes on one side; big established gardens, tall hedges and shaded lawns on the other. We are set up for both.</p>
      <ul class="checks">
        <li>{ICONS['check']} Rated 5.0 on Google</li>
        <li>{ICONS['check']} Every job quoted up front, with the price confirmed before we start</li>
        <li>{ICONS['check']} Mowing, edging, blow-down and waste removal included as standard</li>
        <li>{ICONS['check']} Regular customers get a text the day before each visit</li>
      </ul>
    </div>
    <div class="intro__media reveal" data-d="1"><img src="/assets/img/lawn-mowing.webp" alt="Freshly mown backyard lawn with even stripes, maintained by ONEVISION LAWNS &amp; GARDENS" loading="lazy" width="1200" height="900"><div class="intro__badge"><b>116</b>suburbs covered</div></div>
  </div>
</section>
<section class="section on-dark grain">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">How we work</span><h2>The standard on every job</h2></div>
    <div class="tiles">
      <div class="tile reveal"><span class="icon">{ICONS['calendar']}</span><h3>Booked means booked</h3><p>We keep a schedule. If rain moves it, you hear from us before the day, not after.</p></div>
      <div class="tile reveal" data-d="1"><span class="icon">{ICONS['broom']}</span><h3>The whole job</h3><p>Edges, whipper snipping, blow-down and clippings gone. A mowed lawn with the edges left is half a job.</p></div>
      <div class="tile reveal" data-d="2"><span class="icon">{ICONS['leaf']}</span><h3>Right for the site</h3><p>Cut heights, pruning times, turf varieties and weed treatments chosen for your block, not copied from a template.</p></div>
      <div class="tile reveal" data-d="3"><span class="icon">{ICONS['shield']}</span><h3>No surprises</h3><p>Fixed price per visit. If the scope changes, you hear about the price before the work, not on the invoice.</p></div>
    </div>
  </div>
</section>
{areas_block(light=True)}
{cta_strip()}
{contact_section()}
""" + footer_html()
    write("about/index.html", head(title, meta, path, og_img="/assets/img/work-lawn-pool.webp", schema=schema) + body)

def build_contact():
    title = "Contact ONEVISION | Free Lawn & Garden Quote | 0408 595 570"
    meta = "Free quotes from ONEVISION LAWNS & GARDENS. Call 0408 595 570 or send the form for lawn mowing, garden care, hedges, clean ups, weeds or turf."
    path = "/contact/"
    schema = [local_business(), breadcrumbs([("Home", "/"), ("Contact", path)]), {"@type": "ContactPage", "url": SITE_URL + path, "name": title}]
    body = header_html("contact") + page_hero("Contact ONEVISION for a free lawn or garden quote", f"Call {PHONE}, email, or send the form with your address and what needs doing. Quotes are free, and you hear back the same day in most cases.", [("Home", "/"), ("Contact", path)], "macro.webp", "Central Coast backyard garden at dusk", eyebrow="Get in touch") + contact_section() + f"""
<section class="section on-grey section--tight">
  <div class="wrap">
    <div class="tiles">
      <div class="tile reveal"><span class="icon">{ICONS['clock']}</span><h3>Hours</h3><p>Monday to Saturday from 6am. Quotes answered evenings too.</p></div>
      <div class="tile reveal" data-d="1"><span class="icon">{ICONS['map']}</span><h3>Where we work</h3><p>Central Coast and Sydney's Upper North Shore. <a href="/areas/" class="link-arrow" style="color:var(--green-3)">All 116 suburbs</a></p></div>
      <div class="tile reveal" data-d="2"><span class="icon">{ICONS['star']}</span><h3>Reviews</h3><p>5.0 on Google. <a href="{GMB}" target="_blank" rel="noopener" class="link-arrow" style="color:var(--green-3)">Read them here</a></p></div>
      <div class="tile reveal" data-d="3"><span class="icon">{ICONS['fb']}</span><h3>Facebook</h3><p>Recent jobs and updates. <a href="{FACEBOOK}" target="_blank" rel="noopener" class="link-arrow" style="color:var(--green-3)">Follow ONEVISION</a></p></div>
    </div>
  </div>
</section>
""" + footer_html()
    write("contact/index.html", head(title, meta, path, og_img="/assets/img/macro.webp", schema=schema) + body)

def build_thankyou():
    title = "Quote request received | ONEVISION LAWNS & GARDENS"
    meta = "Your quote request has been received. ONEVISION will be in touch shortly."
    path = "/thank-you/"
    body = header_html("", solid=True) + f"""
<section class="thanks on-dark grain">
  <div>
    <div class="tick">{ICONS['check']}</div>
    <span class="eyebrow">Request received</span>
    <h1 style="font-size:clamp(2rem,4vw,3.2rem)">Thanks, we have got it.</h1>
    <p>{OWNER.split()[0]} will look at what you sent and come back to you with a price, usually the same day. If it is urgent, or you would rather talk it through now, call the number below.</p>
    <div class="actions">
      <a href="tel:{PHONE_RAW}" class="btn btn--primary">{ICONS['phone']} Call {PHONE}</a>
      <a href="/" class="btn btn--ghost">Back to the homepage</a>
    </div>
    <p style="margin-top:36px;font-size:.9rem">While you wait: <a href="/blog/" style="color:var(--green);font-weight:700">read the lawn &amp; garden blog</a> or <a href="{GMB}" target="_blank" rel="noopener" style="color:var(--green);font-weight:700">see our Google reviews</a>.</p>
  </div>
</section>
""" + footer_html()
    write("thank-you/index.html", head(title, meta, path, noindex=True) + body)

def build_privacy():
    title = "Privacy Policy | ONEVISION LAWNS & GARDENS"
    meta = "How ONEVISION LAWNS & GARDENS collects and uses the details you send through this website."
    path = "/privacy/"
    body = header_html("", solid=True) + f"""
<section class="section on-light" style="padding-top:calc(var(--header-h) + 72px)">
  <div class="wrap wrap--narrow prose">
    <span class="eyebrow">Privacy</span>
    <h1 style="font-size:clamp(2rem,4vw,3rem)">Privacy policy</h1>
    <p>ONEVISION LAWNS &amp; GARDENS ({ADDRESS['street']}, {ADDRESS['suburb']} {ADDRESS['state']} {ADDRESS['postcode']}) collects the details you enter into the quote form on this website: your name, email, phone number, property address, property size, the service you need and any job notes. We use them to quote and deliver the work you asked about and to contact you about it.</p>
    <p>Form submissions are stored in our customer relationship management system so we can keep track of your enquiry and job history. We do not sell or share your details with third parties for marketing. This website may use cookies and tracking scripts for analytics and to attribute form submissions.</p>
    <p>To see, correct or delete the details we hold about you, email <a href="mailto:{EMAIL}">{EMAIL}</a> or call {PHONE}.</p>
  </div>
</section>
""" + footer_html()
    write("privacy/index.html", head(title, meta, path, noindex=True) + body)

def build_404():
    title = "Page not found | ONEVISION LAWNS & GARDENS"
    body = header_html("", solid=True) + f"""
<section class="thanks on-dark grain">
  <div>
    <span class="eyebrow">404</span>
    <h1 style="font-size:clamp(2rem,4vw,3.2rem)">That page has been mowed over.</h1>
    <p>The address you followed does not exist on this site. Try the homepage, or call us if you were looking for a quote.</p>
    <div class="actions"><a href="/" class="btn btn--primary">Go to the homepage</a><a href="tel:{PHONE_RAW}" class="btn btn--ghost">{ICONS['phone']} {PHONE}</a></div>
  </div>
</section>
""" + footer_html()
    write("404.html", head(title, "Page not found.", "/404.html", noindex=True) + body)

# ---------------------------------------------------------------------------
# BLOG
# ---------------------------------------------------------------------------
POSTS = [
 {"slug": "lawn-mowing-cost-central-coast", "kw": "lawn mowing cost central coast", "date": "2026-09-22", "img": "lawn-mowing.webp",
  "title": "How Much Does Lawn Mowing Cost on the Central Coast?",
  "meta_title": "Lawn Mowing Cost Central Coast: What Affects the Price",
  "meta": "What lawn mowing costs on the Central Coast, what changes the price, and how regular mowing compares to one-off cuts. Honest local answers from ONEVISION.",
  "excerpt": "Price is the first thing people check. Here is what actually drives the cost of a mow on the coast, and how to pay less per visit.",
  "body": f"""
<p>Lawn mowing cost on the Central Coast is the first thing most people search before they book, and the least clearly answered. Every mowing business prices a little differently, and most will not put a number on a website because no two lawns are the same. This article explains what actually drives the cost of lawn mowing on the Central Coast, so you can tell a fair quote from a bad one.</p>

<h2>What decides the price of a mow</h2>
<p>Five things set the lawn mowing cost for a Central Coast property, and size is only one of them.</p>
<ul>
  <li><strong>Lawn area.</strong> A courtyard lawn in Long Jetty is a very different job to a 900 square metre block in Kariong or an acreage lot in Somersby. Most businesses price in size bands.</li>
  <li><strong>Condition and length.</strong> A lawn on a fortnightly schedule is a quick, clean cut. A lawn that has not been mowed since May takes two passes, blunts blades and produces bags of clippings. One-off cuts on overgrown lawns cost more for that reason.</li>
  <li><strong>Edges and extras.</strong> Edging along paths and beds, whipper snipping around fences and trees, and blowing down hard surfaces add time. Some services quote them as extras; at ONEVISION they are included in every visit.</li>
  <li><strong>Access and terrain.</strong> Steep blocks in Point Clare, Tascott and Killcare Heights, narrow side gates, retaining walls and terraces all slow the job down.</li>
  <li><strong>Frequency.</strong> Regular customers pay less per visit than one-off cuts, because the lawn is easier and the run is planned.</li>
</ul>

<h2>Regular mowing versus one-off cuts</h2>
<p>The biggest lever on your lawn mowing cost is frequency. A fortnightly customer in Erina or Bateau Bay pays a fixed, lower rate per visit because each cut is predictable. A one-off cut on the same lawn after two months of spring growth can cost half as much again, and the lawn looks worse afterwards because it has been scalped back from a great height.</p>
<blockquote>The cheapest lawn to mow is the one that was mowed a fortnight ago.</blockquote>
<p>If you are trying to keep costs down, a fortnightly schedule from September to March and monthly through winter is the sweet spot on the coast. It keeps the lawn healthy, keeps each visit short and keeps your price stable.</p>

<h2>Why franchise and app prices look different</h2>
<p>Franchise mowing services carry territory fees and marketing levies that end up in the per-visit price. Task apps and directories go the other way: cheap headline prices from operators who may not turn up, may not edge and may leave the clippings by the bin. When you compare lawn mowing cost on the Central Coast, compare what is included: edges, whipper snipping, blow-down and green waste removal should all be in the number.</p>

<h2>What is included in an ONEVISION mow</h2>
<p>Every <a href="/services/lawn-maintenance/">lawn maintenance</a> visit from ONEVISION includes mowing at the right height for your grass, edging every hard edge, whipper snipping around obstacles, blowing down paths and driveway, and taking the clippings away. Optional extras like fertilising, aerating and <a href="/services/weed-control/">weed control</a> are quoted separately so you only pay for what you want.</p>

<h2>How to get an accurate quote</h2>
<p>Send us the address, a rough lawn size and how often you want it done. A couple of photos help if the lawn is overgrown. We come back with a fixed price per visit, usually the same day, and that price holds for every visit after unless you change the scope. <a href="/contact/">Request a free lawn mowing quote</a>, or call {PHONE}.</p>
""",
  "faq": [("Is lawn mowing cheaper on a regular schedule?", "Yes. Regular fortnightly or monthly mowing on the Central Coast costs less per visit than one-off cuts because the lawn is shorter, the job is quicker and the run is planned. One-off cuts on overgrown lawns are priced higher to cover the extra passes and clippings."),
          ("Does the lawn mowing price include edging?", "At ONEVISION, yes. Edging, whipper snipping, blowing down hard surfaces and green waste removal are included in every mowing visit. Some other services quote them as extras, so check what a headline price actually covers before comparing.")]},
 {"slug": "best-time-to-lay-turf-central-coast", "kw": "best time to lay turf central coast", "date": "2026-09-22", "img": "turf-installation.webp",
  "title": "When to Lay New Turf on the Central Coast, and Which Grass Copes With Coastal Conditions",
  "meta_title": "Best Time to Lay Turf on the Central Coast + Which Grass",
  "meta": "The best time to lay turf on the Central Coast, month by month, and which grasses handle sand, salt and shade. Practical advice from ONEVISION.",
  "excerpt": "Spring is the window, but the grass you choose matters as much as the month. What works on sandy, salty and shaded coastal blocks.",
  "body": f"""
<p>The best time to lay turf on the Central Coast is spring, from September to November, followed closely by early autumn in March and April. Both give warm soil, mild air temperatures and enough rain to help a new lawn root without daily hosing. Turf can go down in any month on the coast, but the timing changes how much work establishment takes.</p>

<h2>Month by month</h2>
<ul>
  <li><strong>September to November.</strong> The ideal window. Soil is warming, growth is starting and the summer heat has not arrived. Turf laid now is usually rooted in two to three weeks. It is also the busiest time for turf suppliers, so order early.</li>
  <li><strong>December to February.</strong> Fast establishment, but the turf must be watered daily, sometimes twice a day, for the first two to three weeks. Coastal wind in Terrigal, Wamberal and Avoca dries new turf quickly. Only lay in summer if you can commit to the watering.</li>
  <li><strong>March to April.</strong> The second best window. Warm soil, cooler air, less water needed. Lawns laid now are established before winter.</li>
  <li><strong>May to August.</strong> Buffalo and kikuyu will still take, just slowly, and may look patchy until spring. Couch struggles to root in cold soil. Winter laying suits people who want the lawn in before a spring event and can wait for it to thicken.</li>
</ul>

<h2>Which turf suits Central Coast blocks</h2>
<p>The month matters less than matching the grass to the site. Central Coast blocks vary more than most: sand on the Peninsula, clay around Wyong and Tuggerah, salt exposure along the beaches and deep shade in the bush suburbs.</p>
<div class="mini-grid">
  <div class="mini"><b>Sir Walter / Sapphire buffalo</b><span>Handles part shade, salt and most soils. The default for Umina, Terrigal, Erina and anywhere with trees. Low maintenance once in.</span></div>
  <div class="mini"><b>Couch</b><span>Full sun only. Fine leaf, tough under kids and dogs, good for open backyards in Warnervale, Hamlyn Terrace and Woongarrah.</span></div>
  <div class="mini"><b>Kikuyu</b><span>Cheapest and fastest. Suits big sunny blocks and acreage in Somersby, Jilliby and Mangrove Mountain. Invasive near garden beds.</span></div>
</div>
<p>Zoysia is worth a look for premium low-mow lawns, and shade blends exist for gardens under gums. If you are unsure, tell us where the lawn is and how it gets used and we will recommend one.</p>

<h2>Preparation matters more than the calendar</h2>
<p>Turf laid on unprepared ground fails in any month. The old lawn and weeds need to come out, the soil needs hoeing and levelling, sandy sites need organic matter added and clay sites need drainage sorted. A starter fertiliser goes down before the rolls. That preparation is the bulk of a <a href="/services/turf-installation/">turf installation</a> job and the reason a professional lawn outlasts a DIY one.</p>

<h2>Looking after new turf on the coast</h2>
<p>Water so the soil under the turf stays moist, not just the surface, for the first fortnight. Keep foot traffic off it. Give the first mow once you cannot lift a corner, on a high setting. After a month, move to normal mowing and consider a light feed. In coastal wind, watering in the early morning beats the evening.</p>
<p>Planning a new lawn for spring? <a href="/contact/">Get a free turf quote</a> now and we can book you into the September window before it fills.</p>
""",
  "faq": [("Can you lay turf on the Central Coast in winter?", "Yes. Buffalo and kikuyu will root through winter on the Central Coast, just slowly, and the lawn may look thin until spring. Couch is best avoided in cold months. Winter laying works if you can wait for the lawn to thicken and want it in before spring."),
          ("How long should I water new turf?", "Keep new turf moist for the first two weeks, watering daily in spring and up to twice daily in summer, especially in coastal wind. From week three, reduce to every second or third day. Once the turf cannot be lifted at the corner it has rooted and can move to normal watering.")]},
 {"slug": "how-often-to-trim-hedges-north-shore", "kw": "how often to trim hedges north shore", "date": "2026-09-22", "img": "hedge-trimming.webp",
  "title": "How Often Should You Trim Hedges on the Upper North Shore?",
  "meta_title": "How Often to Trim Hedges on the North Shore | ONEVISION",
  "meta": "How often to trim murraya, lilly pilly, photinia, box and conifer hedges on the Upper North Shore, and when in the year to do it. From ONEVISION.",
  "excerpt": "Murraya, lilly pilly, photinia, buxus and conifer all want different treatment. A season-by-season guide for Wahroonga to Roseville.",
  "body": f"""
<p>How often to trim hedges on the North Shore depends on what the hedge is. Fast growers like murraya, lilly pilly and photinia need two to three trims a year to stay dense and straight. Formal box and conifer hedges hold their shape on one or two. Leave any of them for a couple of seasons and you are into a staged reduction rather than a trim, which costs more and looks worse for a year.</p>

<h2>Trimming frequency by hedge type</h2>
<ul>
  <li><strong>Murraya.</strong> The Upper North Shore's front-fence hedge. Trim in late spring after the first flush, again in late summer, and give it a light tidy in autumn. Three trims a year keeps it tight; two keeps it acceptable.</li>
  <li><strong>Lilly pilly.</strong> Similar to murraya but faster in wet years. Two to three trims a year. Watch for psyllid damage on new growth and trim it out.</li>
  <li><strong>Photinia.</strong> Vigorous and prone to going leggy. Two to three trims, and never let it get more than about 30 centimetres above the height you want.</li>
  <li><strong>Viburnum and escallonia.</strong> Two trims a year, spring and late summer.</li>
  <li><strong>Buxus (box).</strong> Once or twice a year, ideally late spring and late summer. Avoid trimming in the heat of the day in January, which scorches the cut leaves.</li>
  <li><strong>Conifers (leighton green, cypress).</strong> Once or twice a year, lightly. Conifers cannot be cut back into bare wood, so the height has to be managed every year rather than fixed later.</li>
</ul>

<h2>When in the year to trim</h2>
<p>On the Upper North Shore, the main trims fall in late October to November and again in late February to March. The spring trim shapes the first flush; the late summer trim tidies the second and sets the hedge up for winter. A light autumn pass in April or May keeps things neat through the slow months. Avoid heavy trimming in midwinter, when cuts stay open longer, and in the hottest weeks of January, when freshly cut foliage burns.</p>
<blockquote>Trim little and often. Every hedge that needs a hard reduction is a hedge that missed a couple of trims.</blockquote>

<h2>Bringing an overgrown hedge back</h2>
<p>If a hedge in Wahroonga, St Ives or Turramurra has got well past its height, it comes down in stages. Most species tolerate losing about a third at a time, so a reduction is spread over two or three trims across a growing season, letting the hedge re-leaf between cuts. Cutting straight back to bare wood in one hit leaves gaps that can take years to fill, or never do on conifers. Our <a href="/services/hedge-trimming/">hedge trimming</a> service handles staged reductions as well as regular trims.</p>

<h2>Put it on a schedule</h2>
<p>The easiest way to keep North Shore hedges right is to stop thinking about them. Most of our customers have hedge trimming built into their <a href="/services/garden-maintenance/">garden maintenance</a> or <a href="/services/lawn-maintenance/">lawn mowing</a> schedule, so the spring and summer trims simply happen. <a href="/contact/">Get a free quote</a> and we will put your hedges on the calendar.</p>
""",
  "faq": [("Can I trim hedges in winter on the North Shore?", "Light tidying is fine, but avoid heavy trimming in June and July. Cuts heal slowly in the cold and frost can damage exposed new growth in Hornsby, Mount Colah and the higher suburbs. Save the main trims for late spring and late summer."),
          ("How much can I cut off a hedge at once?", "About a third of the height or width in one trim for most species, including murraya, lilly pilly and photinia. Conifers should only be lightly trimmed and never cut into bare wood. Larger reductions are done in stages across a growing season.")]},
 {"slug": "spring-garden-clean-up-checklist-central-coast", "kw": "spring garden clean up checklist", "date": "2026-09-22", "img": "clean-ups.webp",
  "title": "The Spring Garden Clean Up Checklist for Central Coast Homes",
  "meta_title": "Spring Garden Clean Up Checklist for Central Coast Homes",
  "meta": "A spring garden clean up checklist for Central Coast homes: lawn, beds, hedges, weeds, paths and gutters, in the right order. From ONEVISION.",
  "excerpt": "September is when coastal gardens get away. Work through this list in order and the yard is ready for summer, or book it out and let us do it.",
  "body": f"""
<p>This spring garden clean up checklist is written for Central Coast gardens, where mild winters mean the weeds never really stopped and September growth arrives all at once. Work through it in this order and the garden is set up for summer. If you get to the end and decide it is a day you would rather not spend, the whole list is what a <a href="/services/garden-clean-ups/">ONEVISION garden clean up</a> covers.</p>

<h2>1. Clear before you cut</h2>
<p>Start by removing what is on the ground: leaf litter from gums and liquidambars, fallen branches, dead annuals and the winter's accumulation of debris in beds and along fences. Raking first means the mower and hedgers are not fighting through it, and it shows you what the beds actually look like.</p>

<h2>2. Weed the beds and paths while the soil is soft</h2>
<p>Spring soil on the coast is still damp, which makes hand weeding easy. Pull oxalis, clover and winter grass from beds now before they flower. Treat paths, pavers and the driveway with a full-kill product so the summer crop does not get started. If the lawn has bindii, it is already late; a selective treatment in September will still reduce the prickles but next winter is the time to hit it properly. See our <a href="/services/weed-control/">weed control</a> page for what works on which weed.</p>

<h2>3. Cut back and prune</h2>
<p>Spring is the time to cut back grasses, salvias and other perennials that have finished, remove frost-damaged tips from tender shrubs, and lift low limbs off paths and lawn edges. Prune spring-flowering shrubs straight after they flower, not before. Roses should already be done by now; if not, do them immediately.</p>

<h2>4. Give hedges their first trim</h2>
<p>Murraya, lilly pilly, photinia and westringia all push hard in September. A trim now sets the shape for the year and keeps the hedge dense. Overgrown hedges come down in stages, not one hit. Our <a href="/services/hedge-trimming/">hedge trimming</a> page explains how.</p>

<h2>5. Mow, edge and feed the lawn</h2>
<p>The first spring mow should be on a high setting to take the top off winter growth without scalping. Re-cut the edges along paths, driveway and beds, which will have blurred over winter. Aerate compacted areas, especially where the kids or dogs run. Then feed. A lawn fertiliser in September, watered in, is the single biggest thing you can do for a good summer lawn. Regular <a href="/services/lawn-maintenance/">lawn mowing</a> from here keeps it that way.</p>

<h2>6. Mulch the beds</h2>
<p>Once beds are weeded and pruned, top up the mulch to 50 to 75 millimetres. On sandy Peninsula blocks this is the difference between beds that survive January and beds that do not. Keep mulch clear of stems and trunks.</p>

<h2>7. Fix what winter broke</h2>
<p>Check irrigation for split lines and blocked drippers before you need it. Reset any edging that has heaved. Re-stake anything the winter westerlies loosened. Clear ground-level gutters and drains of leaf litter so the first summer storm does not flood a bed.</p>

<h2>8. Decide what needs replacing</h2>
<p>Spring is also the best time to replace a lawn that has been beaten by shade, wear or grubs. Turf laid in September and October establishes fastest on the coast. If the lawn is more bare patch than grass, see <a href="/services/turf-installation/">turf installation</a> rather than fighting it for another year.</p>

<h2>Or book the lot</h2>
<p>A full spring clean up on an average Central Coast block is a day's work with a trailer load of green waste at the end. We do it in a single visit, waste included, from Woy Woy to Wyong. September fills quickly, so <a href="/contact/">get a free clean up quote</a> early and lock in a date.</p>
""",
  "faq": [("When should I do a spring garden clean up on the Central Coast?", "Late August to mid September is ideal on the Central Coast. Growth is starting but has not got away, soil is still soft for weeding and hedges are ready for their first shape. Leaving it until October means more cutting, more waste and weeds that have already seeded."),
          ("How long does a spring garden clean up take?", "A DIY spring clean up on an average Central Coast block is usually a full weekend. A professional crew with the right equipment and a trailer does the same job in a single visit, including removing all the green waste, which is the part that eats most of the time.")]},
]

def build_blog():
    # index
    title = "Lawn & Garden Blog | Central Coast & North Shore | ONEVISION"
    meta = "Lawn and garden advice for the Central Coast and Upper North Shore: mowing costs, when to lay turf, hedge trimming and spring clean ups. From ONEVISION."
    path = "/blog/"
    cards = ""
    for i, p in enumerate(POSTS):
        cards += f"""<a href="/blog/{p['slug']}/" class="post-card reveal" data-d="{i%2}">
  <img src="/assets/img/{p['img']}" alt="{esc(p['title'])}" loading="lazy" width="400" height="300">
  <div class="post-card__body"><span class="meta">{p['date']}</span><h3>{esc(p['title'])}</h3><p>{esc(p['excerpt'])}</p><span class="link-arrow" style="color:var(--green-3)">Read the article {ICONS['arrow']}</span></div>
</a>"""
    schema = [local_business(), breadcrumbs([("Home", "/"), ("Blog", path)]), {"@type": "Blog", "url": SITE_URL + path, "name": "ONEVISION lawn and garden blog", "publisher": {"@id": SITE_URL + "/#business"}}]
    body = header_html("blog") + page_hero("Lawn &amp; garden advice for the coast and the North Shore", "Straight answers to the questions we get asked on the job: what things cost, when to do them, and what actually works on Central Coast and Upper North Shore blocks.", [("Home", "/"), ("Blog", path)], "macro.webp", "Close-up of dewy grass blades", eyebrow="Blog") + f"""
<section class="section on-light"><div class="wrap"><div class="posts">{cards}</div></div></section>
{cta_strip()}
{contact_section()}
""" + footer_html()
    write("blog/index.html", head(title, meta, path, schema=schema) + body)

    # posts
    for p in POSTS:
        ppath = f"/blog/{p['slug']}/"
        schema = [local_business(),
                  {"@type": "Article", "@id": SITE_URL + ppath + "#article", "headline": p["title"], "description": p["meta"], "datePublished": p["date"], "dateModified": p["date"],
                   "author": {"@type": "Person", "name": OWNER}, "publisher": {"@id": SITE_URL + "/#business"}, "image": SITE_URL + "/assets/img/" + p["img"],
                   "mainEntityOfPage": SITE_URL + ppath, "keywords": p["kw"]},
                  faq_schema(p["faq"]), breadcrumbs([("Home", "/"), ("Blog", "/blog/"), (p["title"], ppath)])]
        others = "".join(f'<li><a href="/blog/{o["slug"]}/">{esc(o["title"])} {ICONS["arrow"]}</a></li>' for o in POSTS if o["slug"] != p["slug"])
        faqs = "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in p["faq"])
        body = header_html("blog") + page_hero(esc(p["title"]), esc(p["excerpt"]), [("Home", "/"), ("Blog", "/blog/"), (p["title"], ppath)], p["img"], p["title"], eyebrow=f"Published {p['date']} &middot; by {OWNER}") + f"""
<section class="section on-light">
  <div class="wrap layout">
    <article class="prose reveal">{p['body']}<h2>Frequently asked</h2>{faqs}</article>
    <aside class="aside">
      <div class="aside-card"><h3>Want it done for you?</h3><p>Free quotes across the Central Coast and Upper North Shore. Same-day reply in most cases.</p><a href="#quote" class="btn btn--primary">{CTA}</a><a href="tel:{PHONE_RAW}" class="hero__phone">{ICONS['phone']}{PHONE}</a></div>
      <div class="aside-card aside-card--light"><h3>More from the blog</h3><ul class="aside-list">{others}</ul></div>
    </aside>
  </div>
</section>
{cta_strip()}
{contact_section()}
""" + footer_html()
        write(f"blog/{p['slug']}/index.html", head(p["meta_title"], p["meta"], ppath, og_img="/assets/img/" + p["img"], schema=schema) + body)

# ---------------------------------------------------------------------------
# sitemap / robots
# ---------------------------------------------------------------------------
def build_sitemap():
    urls = ["/", "/services/"] + [svc_url(s["slug"]) for s in SERVICES] + ["/areas/", "/areas/upper-north-shore/", "/about/", "/contact/", "/blog/"] + [f"/blog/{p['slug']}/" for p in POSTS]
    pri = {"/": "1.0", "/services/": "0.8", "/areas/": "0.7", "/areas/upper-north-shore/": "0.8", "/about/": "0.5", "/contact/": "0.7", "/blog/": "0.5"}
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        p = pri.get(u, "0.8" if u.startswith("/services/") else "0.6")
        xml += f"  <url><loc>{SITE_URL}{u}</loc><lastmod>2026-09-28</lastmod><changefreq>monthly</changefreq><priority>{p}</priority></url>\n"
    xml += "</urlset>\n"
    write("sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /thank-you/\n\nSitemap: {SITE_URL}/sitemap.xml\n")

# ---------------------------------------------------------------------------
def _photo_img(m):
    """Give every <img> of a client photo its focal point, and (until self-hosted) a Drive URL
    sized for the slot: full-bleed banners (width="1600") get a wider file than cards."""
    tag, key = m.group(0), m.group(1)
    if key not in DRIVE_PHOTOS:
        return tag
    tag = tag.replace("<img ", f'<img style="object-position:{DRIVE_PHOTOS[key]["focus"]}" ', 1)
    if not USE_LOCAL_IMAGES:
        w = 1600 if 'width="1600"' in tag else 1000
        tag = tag.replace(f"/assets/img/{key}.webp", drive_url(key, w))
    return tag

def resolve_images(content):
    content = re.sub(r'<img [^>]*?src="/assets/img/([a-z0-9-]+)\.webp"[^>]*>', _photo_img, content)
    if USE_LOCAL_IMAGES:
        return content
    def url(m):
        k = m.group(1) or m.group(2)
        if k in DRIVE_PHOTOS:
            return drive_url(k, 1200)
        return IMAGES.get(k, m.group(0))
    # The optional SITE_URL prefix (og:image, JSON-LD) is swallowed so remote URLs stay valid.
    return re.sub(re.escape(SITE_URL) + r"/assets/img/([a-z0-9-]+)\.webp|/assets/img/([a-z0-9-]+)\.webp", url, content)

def relativise(rel, content):
    """Turn root-relative hrefs/srcs into page-relative ones so the site works from any
    folder, subdirectory host or opened straight from disk. Absolute https URLs are untouched."""
    depth = rel.count("/")
    prefix = "../" * depth
    content = re.sub(r'((?:href|src|action|data-redirect)=")/(?!/)', lambda m: m.group(1) + prefix, content)
    content = content.replace('href=""', 'href="./"').replace('href="../"' * 0, '')
    if depth == 0:
        content = content.replace('href="" ', 'href="./" ')
    return content

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    content = resolve_images(content)
    if rel.endswith(".html"):
        content = relativise(rel, content)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", rel, f"{len(content)//1024}KB")

def word_stats(html_text, kw):
    m = re.search(r"<main[^>]*>(.*)</main>", html_text, flags=re.S)
    html_text = m.group(1) if m else html_text
    html_text = re.sub(r"<header.*?</header>|<nav class=\"mobile-nav\".*?</nav>", " ", html_text, flags=re.S)
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html_text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = htmlmod.unescape(text)
    words = re.findall(r"[A-Za-z0-9'&]+", text)
    n = len(words)
    k = len(re.findall(re.escape(kw), text, flags=re.I))
    return n, k, (k * len(kw.split()) / n * 100) if n else 0

if __name__ == "__main__":
    home = build_home()
    for s in SERVICES: build_service(s)
    build_services_index(); build_area_uns(); build_areas_index(); build_about(); build_contact(); build_thankyou(); build_privacy(); build_404(); build_blog(); build_sitemap()
    # keyword density report
    print("\n--- keyword density (visible <main> text) ---")
    n, k, d = word_stats(open(ROOT / "index.html").read(), "lawn mowing central coast")
    print(f"home: {n} words, 'lawn mowing central coast' x{k}, {d:.2f}%")
    for s in SERVICES:
        n, k, d = word_stats(open(ROOT / f"services/{s['slug']}/index.html").read(), s["kw"])
        print(f"{s['slug']}: {n} words, '{s['kw']}' x{k}, {d:.2f}%")
    n, k, d = word_stats(open(ROOT / "areas/upper-north-shore/index.html").read(), "gardener north shore")
    print(f"upper-north-shore: {n} words, 'gardener north shore' x{k}, {d:.2f}%")
