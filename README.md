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

**Issues use the real printed covers, and Vol. I has two.** Big Head and Copies
of the Mind are two newsstand versions of one issue, so both appear everywhere
the issue is shown: the front-page hero, the issue map, the store and the issue
page. `printed_pair()` renders the two side by side; `printed()` renders a single
cover for issues that only have one. They are placed whole by the `.cover-stage`
/ `.cover-photo` components, never cropped and never overlaid, because each cover
already carries its own masthead, cover lines and barcode.

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

## Copy that still needs you

Two blocks are placeholders, each flagged in a dashed gold box on the page:

- `about.html`, section `#masthead` — who you are and what *Tripple CH* argues
- `store.html`, section `#book` — the book description

The same two gaps exist in `funnel.html`, marked "Your line goes here".

## Publishing

Any static host works. For GitHub Pages, push the branch and set Pages to serve
from the repository root. `.nojekyll` is already present so the `assets`
directory is served as-is.
