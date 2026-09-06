# Braincopia

The Braincopia magazine site, the Universe Guide, and the six-step sales funnel.
Static HTML, CSS and vanilla JavaScript. No build step, no dependencies, no
framework. Open `index.html` in a browser and the whole thing works.

The magazine takes its structure from Gumroad — hard 1px black rules, offset
block shadows, flat colour panels, oversized display type, sticker labels — and
applies the Braincopia palette and typography on top. The Universe Guide keeps
its own dark treatment, because it is the brand bible rather than the magazine.

**All editorial content follows the Universe Guide.** The seven worlds, the Five
Laws, the Intelligence Principle, the 2025 issue calendar and the Surreal
Mandate are reproduced from it rather than invented. If the guide changes, the
site should be updated to match.

## Pages

| File | What it is |
| --- | --- |
| `index.html` | Front page: manifesto hero, cover story, latest, seven worlds, Five Laws, HI/AI workflow |
| `worlds.html` | The universe map, all seven worlds in full with their tag sets |
| `articles.html` | Full archive, filterable by world |
| `issues.html` | The 2025 calendar, Vol. I through Vol. IV |
| `issue-01.html` | Vol. I contents, seven features across seven worlds |
| `about.html` | Manifesto, why we built this, the Five Laws, masthead, pitch guidelines |
| `store.html` | The 29 tricks, Vol. I, and Tripple CH |
| `universe-guide.html` | The Universe Guide, kept as its own dark single-scroll page |
| `funnel.html` | The six-step funnel |
| `article-*.html` | Ten full articles |
| `404.html` | Not-found page |

## The seven worlds

Articles carry world tags, and the archive filters on them. The tag keys are:

| Key | World |
| --- | --- |
| `fashion` | I — Surreal Fashion & Extreme Design |
| `ai` | II — Artificial & Human Intelligence |
| `business` | III — Visionary Business & Strategy |
| `culture` | IV — Culture, Media & the Zeitgeist |
| `mind` | V — Neuroscience & Philosophy of Mind |
| `futures` | VI — Speculative Design & Visual Futures |
| `desire` | VII — Marketing, Persuasion & the Architecture of Desire |
| `method` | The 29 tricks, the workshop side of the magazine |

Law III means most pieces carry two or three. To file a new article, add its
keys to the `data-tags` attribute on its card in `articles.html` and
`index.html`.

## Structure

```
assets/css/style.css   the whole design system, one file, commented in sections
assets/js/main.js      nav drawer, archive filters, reading progress, forms
assets/img/logo.png       the round badge, lifted off the printed cover
assets/img/logo.svg       earlier placeholder mark, no longer referenced
assets/img/favicon.svg    placeholder favicon
assets/img/cover-vol1-a.jpg  Vol. I cover version A, Big Head
assets/img/cover-vol1-b.jpg  Vol. I cover version B, Copies of the Mind
assets/video/braincopia-vol1.mp4  the Vol. I reel, 1080x1350, 5.6s
assets/video/braincopia-structure.mp4/.webm  the front-page film band
assets/img/structure-poster.jpg   its poster frame
tools/reel/                   source and render script for that reel
```

## The logo

`assets/img/logo.png` is the real badge, supplied as artwork: transparent
background, trimmed to the mark, exported at 512px. `assets/img/favicon.png` is
the same mark at 180px and is what every page loads as its tab icon. Both replace
the placeholders that shipped earlier, and the source is high enough resolution
to re-export larger if you ever need it.

`assets/img/logo-lockup.png` is the full lockup, badge over the green Braincopia
wordmark, trimmed of its white margin. Nothing on the site uses it yet: the
header and footer set BRAINCOPIA in Bebas Neue beside the badge rather than
placing the lockup as one image. Swapping to the lockup means replacing the
`.brand-mark` image and dropping the `.brand-type` block so the name is not set
twice.

## Motion

Two mechanisms, split by browser support.

**Parallax** is JavaScript, in `main.js`, so it runs everywhere. Any element with
`data-parallax="0.14"` shifts against the scroll by that fraction of viewport
height — at 900px tall that is about 138px of travel, which is the point: the
first version multiplied by a flat 100 instead and moved 16px, which nobody could
see. The printed covers drift inside their violet panels, and article cover type
drifts against its panel. It skips under `prefers-reduced-motion`.

`.cover-stage` carries extra vertical padding so a drifting cover never hits the
panel edge and gets clipped. Increase `data-parallax` and that padding together.

**Scroll-driven CSS** is section 13 of the stylesheet, no JavaScript: rack covers
rise onto the shelf left to right, and section rules draw themselves in. These use
`animation-timeline: view()`, so they sit behind `@supports` and only run in
Chromium for now.

An element must never be in both — they would overwrite each other's `transform`.

Everything here rests at its final state and only moves what is already visible.
Nothing is parked at `opacity: 0` waiting to be scrolled into, so with motion off,
support missing or JavaScript disabled the page reads identically.

## The world panels

`worlds.html` presents the seven worlds as full-height rooms, one per world,
after the drakedesign.work reference. Each panel carries four depths that move at
their own rate on scroll:

| Layer | `data-parallax` | Behaviour |
| --- | --- | --- |
| Ground | none | The flat brand colour. Fixed. |
| Big word | `0.055` | The world's name, oversized behind everything, drifts slowest |
| Copy | `0.03` | Headline, description, arrow. Barely moves |
| Card | `0.15` | The tag list. Floats most |

Measured over 500px of scroll those come out at roughly 26px, 15px and 64px —
three genuinely distinct rates, which is what reads as depth.

`WORLD_SKIN` in the build script holds a ground, a text colour and an accent per
world, so each room is its own colour environment while staying inside the brand
palette. The reference uses rounded cards; these are hard-edged with an offset
block shadow, because that is this site's language and the rounded version fought
it.

Anything carrying a layout transform is wrapped in a positioning element — the
parallax script owns `transform` on whatever it moves, so the two cannot share an
element. That is why `.wp-bigtype` sits inside `.wp-bigtype-wrap`.

Each panel's arrow links to `articles.html#<world key>`, and the archive applies
that filter on load.

## Cover proportions

**The magazine is A4, 210 x 297mm, a ratio of 1:1.4143.** `--cover-ratio` in the
stylesheet holds it. Any box drawn to stand in for a cover — the rack slipcases
for unshot issues — takes its shape from that token, never from the pixel
dimensions of a particular export.

Every cover box on the site is A4: the printed covers, the rack items and the
slipcases alike.

`cover-vol1-a.jpg` and `-b.jpg` are 768 x 1362, a ratio of 1:1.7734, about 25%
taller than A4. They are cropped to fit rather than squeezed, via `object-fit:
cover`. `--cover-focus` decides what survives that crop; it is `center top`, which
keeps the masthead and takes roughly a fifth off the bottom of each cover — the
barcode goes with it. Change that token to move the crop.

Re-exporting the two files at A4 from the print artwork removes the crop
altogether and is the proper fix.

## The video header

The front page opens on the film. `.vhero` runs it full-bleed behind the masthead
copy, and it parallaxes: the video is laid out at 128% of the header's height with
a 14% overhang, and JavaScript translates it inside that, so the shift never
uncovers an edge. If you raise its `data-parallax`, raise the overhang with it.

`.vhero-scrim` carries two gradients: one from the left so the copy column keeps a
steady dark ground whatever frame is playing, one from the bottom for the buttons
and stats. The right side stays clear so the film is actually visible.

This replaced both the old split hero and the separate film band lower down, so
the front page went from ten sections to eight.

Two encodes ship, and both are needed. `.mp4` is H.264, which Safari and iOS
require. `.webm` is VP9, for browsers built without proprietary codecs — plenty of
Linux Chromium and Firefox builds have no H.264 decoder, and the source list falls
through to WebM there. MP4 is listed first so Safari takes it.

The source was 5.9MB with an audio track; the web encodes are about 1.9MB each and
silent, since it autoplays. Under `prefers-reduced-motion` it does not autoplay and
holds on its poster frame instead.

## The Vol. I reel

`assets/video/braincopia-vol1.mp4` — 1080x1350, 5.6 seconds, H.264, portrait for
social. Four beats: the mark and wordmark, cover A rising, cover B crossing over
it, then the yellow end band.

It is reproducible rather than hand-made. `tools/reel/reel.html` exposes
`setFrame(n)` and positions everything by frame number rather than wall clock, so
`python3 tools/reel/render.py` screenshots 140 frames in Chromium and pipes them
through ffmpeg to the same file every time. Add `--gif` for a GIF beside it. It
needs playwright and ffmpeg; set `FFMPEG` or `CHROMIUM` if they are not on PATH.

Edit the storyboard timings at the bottom of `reel.html` and re-run.

## Design tokens

Every colour, font and structural value lives in `:root` at the top of
`assets/css/style.css`. Changing the palette is one edit.

| Token | Value | Used for |
| --- | --- | --- |
| `--violet` | `#5B0ECC` | Primary. Links, hero accent, cover artwork |
| `--green` | `#24B574` | Fills: "out now", the guarantee rule, tick marks |
| `--yellow` | `#FFD600` | Highlights, newsletter panel, dark-panel accents |
| `--gold` | `#B8A050` | Book and secondary editorial fills |
| `--ink` | `#1C1C1C` | Text, every border, every block shadow |
| `--paper` | `#F7F4EE` | Page background |

Three tokens exist only for text. `--green-ink`, `--yellow-ink` and `--gold-ink`
are darkened twins used wherever green, yellow or gold appear as words on a light
surface, because the vivid versions fail contrast at label sizes. Use the vivid
colour for fills and rules, the ink twin for type.

Typography: Bebas Neue for display, Playfair Display for editorial and pull
quotes, Libre Baskerville for body, Space Mono for labels. This matches the
Universe Guide's typography section.

## Cover artwork

Two rules, and the split is deliberate.

**Issues live on a rack.** `rack()` renders the newsstand shelf: every cover in a
row on a dark ground, captioned with its volume. Issues that are out link to
their page; issues not yet shot show a `.rack-slip` slipcase carrying the title
and season. There is no control to operate — the whole run is simply visible,
and the shelf scrolls sideways on narrow screens.

It appears in three places. The front page runs it full width directly under the
hero as "On the Shelf". The issue map leads with it. The Vol. I page uses
`rack(only=..., big=True)`, which shows just that issue's two covers at roughly
twice the width.

At desktop and tablet all five covers fit without scrolling; the item width is
tuned so the row clears the 1240px wrap rather than clipping the last cover by a
sliver. If you add a sixth issue, re-check that.

The hero and the store still show one cover whole, via `printed()`.

**Web articles use a typographic panel.** The `.cover` component: a flat colour
panel, a hairline grid, and display type. No stock imagery and no decorative
shapes, per the Surreal Mandate. Articles are not issues, so they do not borrow
the printed treatment.

## Wiring up the real thing

Three places are front-end only and need connecting to your services:

1. **Newsletter forms** — `assets/js/main.js`, the `[data-signup]` handler. Post
   to ConvertKit, Buttondown or Mailchimp, or point the form `action` at your
   provider.
2. **Funnel checkout** — `funnel.html`, the `submitOrder` function. Swap for
   Stripe Hosted Checkout and land the customer back on step 6.
3. **Funnel lead capture** — `funnel.html`, the `submitLead` function.

## Pricing

One price per thing, no tiers, nothing to choose between. `CATALOGUE` in the build
script holds the three products; the funnel sells the method as a single offer.

| Product | Price |
| --- | --- |
| The 29 Tricks | $29 |
| Vol. I — The Parallel Universe (PDF) | $12 |
| Tripple CH | $12 |
| Vol. I in print | £7.90 |

Tripple CH is sold on its own and is deliberately not bundled with anything.

Every purchase carries 30% off wearyour.store, stated once on the store page and
again on the funnel's confirmation step. **No code is issued by anything here** —
that has to be created in the shop before launch, and it is flagged in-page.

The previous four-tier ladder is gone. It priced the Essentials at $0.60 a trick
against the Full System's $1.00, so buying more cost more per unit and there was
no reason to climb; and the $2 tier lost 18% of its value to payment fees.

## Copy that still needs you

Two blocks are placeholders, each flagged in a dashed gold box on the page:

- `about.html`, section `#masthead` — who you are and what *Tripple CH* argues
- `store.html`, section `#book` — the book description
- `store.html`, section `#wear` — what wearyour.store sells. The network here
  blocks that domain, so I linked it without describing it rather than guessing.

The same two gaps exist in `funnel.html`, marked "Your line goes here".

## Publishing

Any static host works. For GitHub Pages, push the branch and set Pages to serve
from the repository root. `.nojekyll` is already present so the `assets`
directory is served as-is.
