# Braincopia

A statement surreal magazine, made in Amman, Jordan.

Static site: one `index.html`, one `styles.css`, one `script.js`, images in
`/assets`. No build tooling, no framework, no dependencies. Open `index.html` and
it works; push it and GitHub Pages serves it as-is.

```
index.html      the whole site, one page
styles.css      the design system
script.js       cart, checkout, motion
assets/         PNGs and the hero film, referenced by relative path
CNAME           custom domain for GitHub Pages
legacy/         the earlier multi-page site, kept for reference
tools/reel/     renders the Vol. I promo video with ffmpeg
```

## Design system

Sticker aesthetic: thick ink borders, hard offset shadows with no blur,
rounded-square corners, cards that lift and tilt on hover.

| Token | Value | Role |
| --- | --- | --- |
| `--violet` | `#5B0ECC` | the brand |
| `--deep` | `#3D0999` | its shadow |
| `--green` | `#24B574` | signal |
| `--yellow` | `#FFD600` | signal |
| `--pink` | `#FF90E8` | accent, ink grounds only |
| `--orange` | `#FF751F` | Wear Your's orange, not Braincopia's |
| `--green-ink` | `#14724A` | green, dark enough to read as text |
| `--yellow-ink` | `#7A6100` | yellow, ditto |
| `--error` / `--error-bg` | `#B3261E` / `#FCECEA` | semantic, outside the brand set |
| `--ink` | `#1C1C1C` | |
| `--paper` | `#F7F4EE` | |
| `--cream` | `#FFFFFF` | |
| `--line` | `rgba(28,28,28,0.14)` | |

Anton for display, Archivo for headings and body, Space Mono for eyebrows,
labels and prices. Borders are `--border-w: 2.5px solid var(--ink)`, corners
`--radius: 20px`, shadows `7px 7px 0 var(--ink)` growing to `11px` on hover with
a `-4px/-4px` translate and a ±0.6° tilt.

**Per-card theming.** Any card takes `style="--card-color:var(--token)"`, which
drives its heading colour, its price and its links. That is how one grid holds
several colour identities without a class per colour.

**The hero film.** `assets/video/braincopia-structure.mp4` plays behind the
masthead, muted and looping, with a WebM alongside it because not every browser
build ships an H.264 decoder — MP4 first so Safari takes it. The video is laid
out 116% of the hero's height and offset upward so no edge is ever uncovered,
and a two-axis scrim keeps the type legible over any frame. Under
`prefers-reduced-motion` the offset collapses to a plain full-height frame.

**Sulayma.** The ambassador band runs full width and she stands on its
bottom edge, not inside a panel. Her PNG is the supplied artwork with the
white background flood-filled to transparency from the edges, plus the one
enclosed pocket between her arm and torso cleared by its own pixels — a
seed-point fill there lands on line work and eats into the drawing. The
PNG ships close to native size (769px wide, quantised to 256 colours to
keep it near 600KB): her outlines are thin, and pre-scaling costs weight
the browser cannot put back, which is what makes them read olive over the
yellow instead of black.

**The covers.** The two Vol. I covers run at their native proportion inside the
issue section — no crop, no letterbox, no panel behind them. Nothing is drawn
around the artwork but its own ink edge and the hard shadow.

## Motion

`prefers-reduced-motion: reduce` collapses every animation and transition to
0.001ms globally, stops the marquee, holds the hero chant on one line, and shows
all reveals immediately.

Scroll reveals use IntersectionObserver with staggered `nth-child` delays. If
JavaScript never runs, a `<noscript>` block forces `.reveal` back to full opacity
— otherwise every reveal element would sit invisible below the hero.

## Cart and checkout

The cart lives in `localStorage` under `braincopia.cart.v1`, and is re-validated
against the catalogue on load, so an edited or stale entry cannot inject an
unknown product or a negative quantity.

Two deliberate choices in the checkout:

**No contact details in the page.** There is no `mailto:`, no `tel:`, no `wa.me`
anywhere in the source. Both forms POST to Formspree with `fetch` + `FormData`
and an `Accept: application/json` header, so the real inbox only ever exists in
the Formspree dashboard. The view advances to the confirmation **only** on
`res.ok`; anything else leaves the customer on the form with an inline error and
their cart intact.

**The order summary is built with `textContent`, node by node** — never assembled
as an HTML string. It echoes back the name and address the customer typed, so
string concatenation there would be an injection vector.

### The form endpoint

`FORMSPREE_ENDPOINT` at the top of `script.js` holds the Formspree form id. Both
the checkout and the contact form POST to it. The real inbox lives in the
Formspree dashboard and never appears in the page source — that is the whole
point of routing through it. To move the mail somewhere else, change the id
there; nothing else needs touching.

## Deploying

GitHub Pages, from the `main` branch, root folder. `CNAME` holds `braincopia.com`
— change it if the domain differs.

DNS at your registrar:

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `<user>.github.io` |

Then enable **Enforce HTTPS** in the repository's Pages settings once the
certificate is issued.

## A note on the images

The spec asks for PNGs, so that is what ships. The two covers are photographic
and cost about 900KB each as PNG; the same images as JPEG or WebP would be
roughly a tenth of that with no visible difference. Worth switching if page
weight matters.
