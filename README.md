# Braincopia

A statement surreal magazine, made in Amman, Jordan.

Static site: one `index.html`, one `styles.css`, one `script.js`, images in
`/assets`. No build tooling, no framework, no dependencies. Open `index.html` and
it works; push it and GitHub Pages serves it as-is.

```
index.html      the whole site, one page
styles.css      the design system
script.js       cart, checkout, motion
assets/         PNGs, referenced by relative path
CNAME           custom domain for GitHub Pages
legacy/         the earlier multi-page site, kept for reference
tools/reel/     renders the Vol. I promo video with ffmpeg
```

## Design system

Sticker aesthetic: thick ink borders, hard offset shadows with no blur,
rounded-square corners, cards that lift and tilt on hover.

| Token | Value |
| --- | --- |
| `--green` | `#2b5d1c` |
| `--teal` | `#0e93a4` |
| `--purple` | `#5b23e8` |
| `--red` | `#8a1414` |
| `--orange` | `#f3701c` |
| `--yellow` | `#f5c518` |
| `--ink` | `#16150f` |
| `--paper` | `#faf6ea` |
| `--cream` | `#ffffff` |
| `--line` | `rgba(22,21,15,0.14)` |

Anton for display, Archivo for headings and body, Space Mono for eyebrows,
labels and prices. Borders are `--border-w: 2.5px solid var(--ink)`, corners
`--radius: 20px`, shadows `7px 7px 0 var(--ink)` growing to `11px` on hover with
a `-4px/-4px` translate and a ±0.6° tilt.

**Per-card theming.** Any card takes `style="--card-color:#hex"`, which drives its
heading colour, its price and its links. That is how one grid holds six different
colour identities without six classes.

**Stickers.** `.sticker` is a rotated pill with a border and hard shadow, wobbling
on a 3.4s loop. `.sticker-soon` and `.sticker-limited` change only the fill.
Cards deliberately do not clip: the sticker sits 19px above the card's top edge,
so `.collection` has no `overflow: hidden` and the rounding lives on
`.collection-media` instead.

## Motion

`prefers-reduced-motion: reduce` collapses every animation and transition to
0.001ms globally, stops the marquee, holds the hero chant on one line, and shows
all reveals immediately.

Scroll reveals use IntersectionObserver with staggered `nth-child` delays. If
JavaScript never runs, a `<noscript>` block forces `.reveal` back to full opacity
— otherwise 24 elements would sit invisible below the hero.

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
