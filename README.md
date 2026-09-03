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
assets/img/logo.svg    placeholder logo mark
assets/img/favicon.svg placeholder favicon
```

## Swapping in the real logo

The logo shipped here is a **placeholder**. Replace these two files and every
page picks up the change with no edits to any HTML:

- `assets/img/logo.svg` — the nav and footer mark, square, `viewBox="0 0 64 64"`
- `assets/img/favicon.svg` — the browser tab icon

If your logo is a PNG, drop it in as `assets/img/logo.png` and find-and-replace
`assets/img/logo.svg` across the `.html` files. For a wide wordmark rather than a
square mark, widen `.brand-mark` in the stylesheet and remove the `.brand-type`
block from the header so the name is not set twice.

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

No stock imagery anywhere, per the Surreal Mandate. Article and issue covers are
generated in CSS from a flat colour panel, overlapping geometric shapes and
display type — the `.cover` component in the stylesheet. To use real artwork
instead, put an `<img>` inside `.cover` with `position:absolute; inset:0;
object-fit:cover`.

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
