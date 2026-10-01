# MEAE NEWS — Telegram media-monitoring bot

A Telegram bot, in **English and Arabic**, that tells people within minutes when
a name they follow (a company, brand, organisation or person) is mentioned in
online news across the **Middle East and Asia**: the Gulf, Levant, Egypt, Iraq,
Iran, Yemen, Turkey, Afghanistan, Bangladesh and Myanmar.

## What users get

- **Instant alerts**: every news source is checked every 3 minutes, so alerts
  arrive within about 5 minutes.
- **Daily digest**: instead of (or as well as) instant alerts, at the hour and
  time zone the user chooses.
- **English and Arabic in one keyword**: `Aramco, أرامكو, Saudi Aramco, -stock`
  follows all three spellings and skips articles that mention "stock".
- **Arabic-aware matching**: diacritics and spelling variants (أ/إ/ا, ة/ه, ى/ي)
  don't matter, and attached prefixes are found (وأرامكو, لأرامكو, بالجزيرة).
- **Search**: articles from the last 30 days that the bot has collected.
- **Free**, up to 10 keywords per person (`MAX_KEYWORDS_PER_USER`).
- The interface follows the user's Telegram language, and can be switched in
  Settings. The bot's profile ("What can this bot do?") is in both languages.

Sources: about 100 RSS feeds (listed in `bot/sources.py`), plus a **Google
News** search for every keyword. Google News also finds mentions inside the
article text and in outlets that aren't on the list.

## 1. Create the bot in Telegram (5 minutes)

1. In Telegram, open **@BotFather** and send `/newbot`.
2. Name: `MEAE NEWS`. Username: anything ending in `bot`, e.g. `MEAENewsBot`.
3. BotFather replies with a **token** like `123456789:AAH...`. Keep it secret.
4. Optional: `/setuserpic` to upload a logo.

The bot sets its own description, short description and command menu in both
languages when it starts. You don't need to do that in BotFather.

To find your own Telegram user id (for admin commands), message **@userinfobot**.

## 2. Run it on a server

The bot must run 24/7, so it needs an always-on machine. A small VPS is
enough: 1 CPU, 1 GB RAM (Hetzner, DigitalOcean, Contabo and similar, about
$5/month).

### With Docker (recommended)

```bash
git clone <this repository>
cd meae-news-bot
cp .env.example .env
nano .env                       # paste BOT_TOKEN and your ADMIN_IDS
docker compose up -d --build    # start, and restart automatically
docker compose logs -f          # watch it work
```

The database is kept in `./data/`. To update: `git pull && docker compose up -d --build`.

### Without Docker

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in BOT_TOKEN and ADMIN_IDS
python -m bot
```

Python 3.11 or newer. To keep it running, use a `systemd` service or `screen`.

### Platforms like Railway or Render

These work too: deploy the `Dockerfile`, set `BOT_TOKEN` and `ADMIN_IDS` as
environment variables, and **attach a persistent volume at `/app/data`**.
Without a volume, users and keywords are lost on every redeploy.

## 3. Check the news sources (do this once)

News sites sometimes move their RSS feeds. On the server, run:

```bash
docker compose run --rm bot python -m bot.check_feeds    # or: python -m bot.check_feeds
```

It lists which feeds work. Fix or delete the broken ones in `bot/sources.py`
(each one is a single line), then restart. While running, the bot also keeps
track of failing feeds: send it `/feeds`.

To add a source, add a line to `bot/sources.py`:

```python
Feed("Name shown in alerts", "https://site.com/rss", "ar", "SA"),
```

## Admin commands

Only for user ids in `ADMIN_IDS`:

| Command | What it does |
|---|---|
| `/stats` | users, keywords, articles collected, alerts in the last 24h |
| `/feeds` | sources that are failing, and why |
| `/broadcast <text>` | send a message to every user |

## Settings (`.env`)

| Variable | Default | Meaning |
|---|---|---|
| `BOT_TOKEN` | — | token from @BotFather (required) |
| `ADMIN_IDS` | — | admin Telegram user ids, comma-separated |
| `MAX_KEYWORDS_PER_USER` | 10 | free keyword limit |
| `POLL_INTERVAL_SECONDS` | 180 | how often RSS feeds are checked |
| `GOOGLE_NEWS_ENABLED` | true | also search Google News per keyword |
| `GOOGLE_NEWS_INTERVAL_SECONDS` | 600 | how often Google News is searched |
| `MAX_ARTICLE_AGE_HOURS` | 12 | older articles are kept for search but not alerted |
| `RETENTION_DAYS` | 30 | how long articles are kept for search |
| `DEFAULT_TIMEZONE` | Asia/Riyadh | digest time zone for new users |

## How it works

```
bot/
  __main__.py     start-up: Telegram connection, profile texts, background loops
  handlers.py     the chat: menu, keywords, search, settings, admin commands
  engine.py       polling loops, matching, alerts, daily digests, clean-up
  fetcher.py      downloading RSS feeds and Google News searches
  textnorm.py     English/Arabic normalisation and keyword matching
  i18n.py         every message in English and Arabic
  sources.py      the list of news sources
  db.py           SQLite storage
  check_feeds.py  tests which sources work
```

- The first time a feed is read, or a keyword is searched on Google News,
  the existing articles are saved (for search) but **not** alerted. Only news
  that appears after that triggers alerts, so a new user doesn't get flooded.
- Each article is sent to each user at most once, even if several keywords
  match. A story found both on a site and through Google News is sent once.
- If a user blocks the bot, sending to them stops. It resumes if they press Start again.

## Limits of this version

- **RSS feeds contain only the headline and a summary.** A name that appears
  only deep inside an article is found through Google News, not the site's own
  feed. Fetching the full text of every article is possible later.
- **Google News** is unofficial and free. With thousands of keywords, Google
  may start rate-limiting. Increase `GOOGLE_NEWS_INTERVAL_SECONDS`, or switch
  to a paid news API.
- **Languages of the sources**: English and Arabic only. Turkish, Persian/Dari,
  Pashto, Bengali and Burmese-language outlets can be added later, but users
  would then need to add keywords in those languages too.
- **Social media** (X/Twitter, Facebook, YouTube, Telegram channels) isn't
  included yet. Telegram channels are the cheapest to add next.

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

The tests cover matching, both languages, the full chat flow (with a fake
Telegram connection), alerts, digests and feed polling.
