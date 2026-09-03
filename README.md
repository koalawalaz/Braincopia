# Braincopia

A magazine website for **Braincopia — HI / AI**, plus the six-step sales funnel.
Static HTML, CSS and vanilla JavaScript. No build step, no dependencies, no framework.
Open `index.html` in a browser and the whole site works.

The design borrows its structure from Gumroad — hard 1px black rules, offset block
shadows, flat colour panels, oversized display type, sticker-style labels — and
applies the Braincopia palette and editorial typography on top.

## Pages

| File | What it is |
| --- | --- |
| `index.html` | Front page: hero, cover story, latest, disciplines, Five Laws, newsletter |
| `articles.html` | Full archive with client-side filtering by discipline |
| `issues.html` | Issue shelf: Issue 01 out now, 02 and 03 upcoming |
| `issue-01.html` | Issue 01 contents, all seven features |
| `about.html` | What the magazine is, the Five Laws, masthead, pitch guidelines |
| `store.html` | The four trick sets, Issue 01, and Tripple CH |
| `funnel.html` | The six-step funnel, unchanged apart from a link back to the magazine |
| `article-*.html` | Six full articles |
| `404.html` | Not-found page |

## Structure

```
assets/css/style.css   the whole design system, one file, commented in sections
assets/js/main.js      nav drawer, archive filters, reading progress, forms
assets/img/logo.svg    placeholder logo mark
assets/img/favicon.svg placeholder favicon
```

## Swapping in the real logo

The logo shipped here is a **placeholder**. Replace these two files and every page
picks up the change with no edits to any HTML:

- `assets/img/logo.svg` — the nav and footer mark, square, `viewBox="0 0 64 64"`
- `assets/img/favicon.svg` — the browser tab icon

If your logo is a PNG rather than an SVG, drop it in as `assets/img/logo.png` and
run a find-and-replace across the `.html` files for `assets/img/logo.svg`.
For a wide wordmark rather than a square mark, widen `.brand-mark` in
`assets/css/style.css` (search for `.brand-mark`) and remove the `.brand-type`
block from the header markup so the name is not set twice.

## Design tokens

Every colour, font and structural value lives in `:root` at the top of
`assets/css/style.css`. Changing the palette is one edit.

| Token | Value | Used for |
| --- | --- | --- |
| `--violet` | `#5B0ECC` | Primary. Links, hero accent, cover artwork |
| `--green` | `#24B574` | Confirmation, guarantee, "out now" |
| `--yellow` | `#FFD600` | Highlights, newsletter panel, dark-panel accents |
| `--gold` | `#B8A050` | Book and secondary editorial |
| `--ink` | `#1C1C1C` | Text, every border, every block shadow |
| `--paper` | `#F7F4EE` | Page background |

Typography: Bebas Neue for display, Playfair Display for headlines, Libre
Baskerville for body, Space Mono for labels. All four load from Google Fonts.

## Cover artwork

No stock imagery anywhere. Article and issue covers are generated in CSS from a
flat colour panel, overlapping geometric shapes and display type — the `.cover`
component in the stylesheet. To use a real image instead, put an `<img>` inside
`.cover` and give it `position:absolute; inset:0; object-fit:cover`.

## Wiring up the real thing

Three places are front-end only and need connecting to your services:

1. **Newsletter forms** — `assets/js/main.js`, the `[data-signup]` handler. Post to
   ConvertKit, Buttondown or Mailchimp, or point the form `action` at your provider.
2. **Funnel checkout** — `funnel.html`, the `submitOrder` function. Swap for Stripe
   Hosted Checkout and land the customer back on step 6.
3. **Funnel lead capture** — `funnel.html`, the `submitLead` function.

## Copy that still needs you

Two blocks are deliberately marked as placeholders, both flagged in a dashed gold
box on the page itself:

- `about.html`, section `#masthead` — who you are and what *Tripple CH* argues
- `store.html`, section `#book` — the book description

The same two gaps exist in `funnel.html`, marked "Your line goes here".

## Publishing

Any static host works. For GitHub Pages, push the branch and set Pages to serve
from the repository root. `.nojekyll` is already present so the `assets` directory
is served as-is.
