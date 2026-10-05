# OneVision Lawns & Gardens — website

Static, dependency-free site built from the Step 1 SEO research report. Every page's `<title>`, meta description, H1 and target keyword is implemented verbatim from that report.

## Build

```
python3 build.py
```

`build.py` holds all copy, the keyword map, schema and shared chrome and writes the HTML. Edit copy there, re-run, commit the output. Nothing to install (Python 3 standard library only).

## Structure

| Path | Target keyword |
|---|---|
| `/` | lawn mowing central coast |
| `/services/lawn-maintenance/` | lawn mowing hornsby |
| `/services/garden-maintenance/` | garden maintenance central coast |
| `/services/turf-installation/` | turf laying central coast |
| `/services/hedge-trimming/` | hedge trimming north shore |
| `/services/garden-clean-ups/` | garden clean up central coast |
| `/services/weed-control/` | weed control central coast |
| `/areas/upper-north-shore/` | gardener north shore |
| `/areas/`, `/services/`, `/about/`, `/contact/`, `/blog/` + 4 posts, `/thank-you/` (noindex), `/privacy/`, `404.html` | supporting |

Pages are folders with an `index.html` so URLs match the report (`/services/lawn-maintenance`). All asset and link paths are page-relative, so the site works from the domain root, a subfolder, or opened straight from disk (double-click `index.html`; folder links and the form redirect resolve to the right `index.html`). Host on anything static (Netlify, Vercel, Cloudflare Pages, GHL custom hosting, cPanel). Point 404s at `404.html`.

## Areas map

`areamap.py` draws the service-area map as inline SVG from approximate suburb centroids (coastline draws itself, suburb dots pop in, a marker runs the M1 between the regions, hovering a suburb name lights its dot, the legend focuses a region). The full suburb lists stay in the page as text inside collapsible `<details>` blocks so the local-SEO signal from the report is unchanged.

## Brand

- Green sampled from the supplied logo file: `#6AC03E` (the brief estimated `#4CB749`; the file is lighter). Defined once as `--green` in `assets/css/site.css`.
- Black `#0A0A0A`, white, neutral greys only. No other accent.
- Headings: Montserrat 800/900 (matches the wordmark). Body: Manrope. Loaded from Google Fonts.
- `assets/img/logo.jpg` is the supplied badge untouched (resized only). `assets/img/logo.png` is the knockout version: same badge with the area outside the green ring made transparent, for light backgrounds. `favicon.png` / `logo-180.png` are crops of the same file.

## Forms and CRM

Every quote form (`form.quote-form`) posts these field names, which map 1:1 to the GoHighLevel contact fields:

| Input `name` | GHL field |
|---|---|
| `full_name` | `{{contact.full_name}}` |
| `email` | `{{contact.email}}` |
| `phone` | `{{contact.phone}}` |
| `property_address` | `{{contact.property_address}}` |
| `property_size` | `{{contact.property_size}}` |
| `service_needed` | `{{contact.service_needed}}` |
| `job_notes` | `{{contact.job_notes}}` |

The GHL external tracking script (`tk_98eb122384f74f4bbfd3a2e2026b2166`) is loaded in the `<head>` of every page and captures the submit event. There is no form endpoint: the site's submit handler runs in the capture phase (so no third-party listener can swallow it), lets the tracking script's own listener see the submission, pushes a `quote_form_submit` event to `dataLayer`, shows a spinner, then redirects to the thank-you page after 700ms. If anything blocks the submit event, a click safety net still runs the same flow. A hidden honeypot field (`ov_trap`, `display:none` so browser autofill can never touch it) flags bots: they still see the thank-you page but are not counted as a lead in `dataLayer`.

## QA

`python3 -m http.server 8787` then open the site. The build was checked in headless Chromium (Playwright) at 1440px and on an iPhone 13 profile: one H1 per page, title and description lengths, canonical, schema present, tracking script present, Services mega-dropdown on hover and tap, frosted header on scroll, all internal links resolve, mobile burger and Services accordion, sticky call bar, no horizontal overflow, and both quote forms redirect to `/thank-you/`.

## Before launch (open items)

1. **Domain.** `SITE_URL` in `build.py` is a placeholder (`onevisionlawnsandgardens.com.au`). Set the real domain, rebuild. It drives canonicals, `og:url`, schema `@id`s and `sitemap.xml`.
2. **Phone number.** Resolved: the site now uses `0408 595 570`, matching the Google Business Profile. Change it in one place (`PHONE` / `PHONE_RAW` in `build.py`) if it ever moves.
3. **Hero video.** Hot-linked from the Higgsfield CDN (`HERO_VIDEO_URL` in `build.py`). Download it, put it at `assets/video/hero.mp4` and point the constant there. The poster image is local so the hero still works if the link dies.
4. **Photos.** All imagery is AI-generated (Higgsfield). The build environment could not reach the Higgsfield CDN, so pages currently reference the full-resolution originals there (1.5 to 2.7 MB PNGs each, too heavy for production). Run `python3 tools/fetch_assets.py` on any normal machine to pull them into `assets/img/` as optimised WebP, set `USE_LOCAL_IMAGES = True` in `build.py`, rebuild and commit. Swap in real job photos as they come through; job IDs are in `docs/assets.md`.
5. **FAQ answers and pricing language** were drafted without Lachlan's input. Confirm scope, schedules and the "text the day before" promise before go-live.
6. **Insurance / ABN.** Not stated on the site because not supplied. Add to footer and About once confirmed.
7. **Reviews.** No review text was supplied, so the site links to Google rather than quoting. Add verbatim reviews to the proof section when available.
8. **Open Graph image.** `assets/img/og-home.jpg` is referenced but not yet created; supply a 1200x630 image or the hero will be used by most platforms via the page image.
9. Verify the GHL tracking script is recording submissions on the live domain (submit a test enquiry and check the contact appears with all seven fields).
