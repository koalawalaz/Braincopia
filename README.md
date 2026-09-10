# Braincopia

A statement surreal magazine, made in Amman, Jordan.

Static site: one `index.html`, one `styles.css`, one `script.js`, images in
`/assets`. No build tooling, no framework, no dependencies. Open `index.html` and
it works; push it and GitHub Pages serves it as-is.

```
index.html      the magazine
styles.css      the magazine's design system
script.js       cart, checkout, motion
studio.html     the agency page: services, packages, brief
studio.css      the studio page's styles
studio.js       the service picker, presets, brief form
site.css        chrome shared by every page: loader, die, sound
site.js         the same, in behaviour
assets/         PNGs and the hero film, referenced by relative path
CNAME           custom domain for GitHub Pages
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

**The founder's plate.** The painting beside the letter is 412x512 at
source, so the column is capped near that rather than blown up soft. If a
larger original turns up, swap the file and raise the cap.

**The covers.** The two Vol. I covers run at their native proportion inside the
issue section — no crop, no letterbox, no panel behind them. Nothing is drawn
around the artwork but its own ink edge and the hard shadow.

## Motion

`prefers-reduced-motion: reduce` collapses every animation and transition to
0.001ms globally, stops the marquee, holds the hero chant on one line, and shows
all reveals immediately.

**One set of chrome, every page.** The loader, the rolling die and the sound
toggle live in `site.css` and `site.js`, which both pages load before their
own. They are styled only through tokens each page already declares, so the
furniture takes whichever palette it lands in. `site.js` exposes
`braincopia.ready(fn)` for anything that must wait for the overlay to leave.
The sound preference is one `localStorage` key for the whole origin, so
switching it off on one page keeps it off on the next.

**The loader.** A held breath, not a performance: the logo mark scales and
fades in over 340ms, holds, and the overlay fades out, gone inside 900ms.
It locks scrolling while it is up and releases it on every exit path,
finishing, a click to skip, or the timer that force-finishes so the page
can never be trapped. It hands over with a `braincopia:ready` event, which
the die waits for rather than bouncing behind the overlay. No loader at all
under `prefers-reduced-motion`, and the `<noscript>` block hides it since
nothing would be left to remove it.

**Sound.** `assets/audio/ambience.mp3` loops behind the page. Browsers
refuse to start audio before the visitor has interacted, so the site tries
to play on load and, when the browser says no, starts on the first click,
key or touch instead. The toggle at bottom right is always on screen,
because a page that makes noise owes you a way to stop it. It shows as
soon as the page loads and only takes itself away if the file actually
fails: gating it on `canplaythrough` hid it permanently on iOS, which
does not fetch media until the visitor interacts, so the event never
fired. It keeps the word at every width: hiding it on a phone left
the bars alone in a square, which turned the pill into a circle and made
the tap target 46x37, under the 44px a finger needs. turning it off
is remembered in `localStorage` and it never auto-starts again. It pauses
on a hidden tab and fades in and out over 900ms rather than cutting.

The current track is a placeholder generated by
`tools/audio/make-ambience.py`: filtered noise over a low drone with bells
struck off the grid, 45 seconds, written from scratch so nothing in it is
anyone else's recording. Every modulation completes a whole number of
cycles across the loop and the tail crossfades into the head, so it
repeats without a seam. Replace the mp3 with the real track and nothing
else needs changing.

**The die.** A die rolls along the bottom of the window as the page
scrolls: the scroll position told as an object rather than a bar. A square
does not spin as it rolls, it pivots on one corner at a time, so over each
quarter turn the centre swings on an arc of radius `side/√2` about the
resting corner and the die advances exactly one side length. Travel comes
from scroll progress and the rotation is derived from the travel, never the
reverse, or it skids. On load it drops in and bounces itself to rest
first: each impact keeps 46% of the speed it arrived with, so the hops
shrink the way a real one does, and the whole spin is spent on the way
down so it lands flat on a face. Scrolling during the drop hands over to
the scroll immediately, and opening the page part-way down (a reload, a
#link) skips the drop entirely. The face changes mid-tumble, while the die is up on a
corner and the top face is edge-on, so the number is never seen to swap. It
is `pointer-events: none`, sits under the cart drawer, and does not exist at
all under `prefers-reduced-motion`.

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

**Recurring lines.** A catalogue entry with a `period` is a subscription
and carries `max: 1`, because nobody holds two of the same monthly plan.
Totals are kept apart rather than summed: a basket with the book and a
subscription reads `$12 + $7 / month`, never `$19`, which would tell
someone they are paying once what they are paying every month.

**The checkout does not take money.** It posts an order to Formspree,
which is fine for a one-off but cannot bill anyone monthly. A real
subscription needs a processor that does recurring charges.

**The order summary is built with `textContent`, node by node**, never assembled
as an HTML string. It sits beside fields the customer typed into, so string
concatenation there would be an injection vector.

**Nothing ships.** Both products are digital, so the checkout asks for a name
and an email and nothing else. There is no address field to fill in or to
echo back.

### The form endpoint

`FORMSPREE_ENDPOINT` at the top of `script.js` holds the Formspree form id. Both
the checkout and the contact form POST to it. The real inbox lives in the
Formspree dashboard and never appears in the page source — that is the whole
point of routing through it. To move the mail somewhere else, change the id
there; nothing else needs touching.

## Deploying

GitHub Pages, from the `main` branch, root folder. `CNAME` holds
`braincopia.com`; change it if the domain differs.

DNS at the registrar. The four A records point the apex at GitHub's Pages
servers, the four AAAA records do the same over IPv6, and the CNAME sends
`www` to the same site:

| Type | Name | Value | TTL |
| --- | --- | --- | --- |
| A | `@` | `185.199.108.153` | 3600 |
| A | `@` | `185.199.109.153` | 3600 |
| A | `@` | `185.199.110.153` | 3600 |
| A | `@` | `185.199.111.153` | 3600 |
| AAAA | `@` | `2606:50c0:8000::153` | 3600 |
| AAAA | `@` | `2606:50c0:8001::153` | 3600 |
| AAAA | `@` | `2606:50c0:8002::153` | 3600 |
| AAAA | `@` | `2606:50c0:8003::153` | 3600 |
| CNAME | `www` | `koalawalaz.github.io` | 3600 |

All four A records are needed, not one of them: they are alternative routes
to the same site. Delete any other A, AAAA or CNAME on `@` or `www` first,
including a registrar parking page, or they will fight. Never put a CNAME on
the apex.

In the repository, Settings → Pages: source `main` / root, custom domain
`braincopia.com`, then tick **Enforce HTTPS** once the certificate is issued,
which takes a few minutes after DNS resolves.

## A note on the images

The spec asks for PNGs, so that is what ships. The two covers are photographic
and cost about 900KB each as PNG; the same images as JPEG or WebP would be
roughly a tenth of that with no visible difference. Worth switching if page
weight matters.
