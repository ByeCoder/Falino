<p align="center"><img src="assets/falino-avatar.png" width="144" alt="Falino smiling moon"></p>

# Falino ✨ | فالینو

**A friendly daily ritual, with a practical administration toolkit.**

[![CI](https://github.com/ByeCoder/Falino/actions/workflows/ci.yml/badge.svg)](https://github.com/ByeCoder/Falino/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB)
![Telethon](https://img.shields.io/badge/Telegram-Telethon-26A5E4)

**[English](README.md) · [راهنمای کامل فارسی](README.fa.md)** · [Installation](#quick-start) · [Administration](#administration) · [Development](#development) · [Publishing](docs/PUBLISHING.fa.md)

Falino is a self-hosted Telegram horoscope and tarot bot. It receives updates
through **Telethon**, sends styled keyboards through the HTTP Bot API, and keeps
profiles, schedules, tickets and statistics in **SQLite WAL**. One asynchronous
process handles the bot; no Redis, browser scraper or separate web panel is needed.

## Features

| Area | Included |
|---|---|
| Readings | Daily, weekly and monthly zodiac readings; editor-published annual content; daily tarot and a three-card spread |
| Birth profile | Gregorian/Solar Hijri dates, Persian/Arabic/Hindi numerals, automatic or manual zodiac selection, nickname |
| Daily delivery | Explicit opt-in, user-selected time/timezone, stop controls, birthday greeting within the subscribed delivery |
| Channel publishing | Independent hourly schedules, twelve-sign digests, full readings, preview/pause/delete controls |
| Mandatory membership | Multiple public/private channels; total-member or verified-new-join goals; automatic completion and duplicate-credit protection |
| Administration | `/panel`, user search/dossiers, restrictions, campaigns, confirmed/resumable broadcasts, queue status |
| Statistics | Tehran local days, Saturday-start weeks, Jalali months and all-time totals; distinct active profiles and successful readings by type |
| Support | Two-way tickets, staff-group replies, attachments, private admin inbox fallback, internal notes, user-owned ticket history |
| Audit logs | Private staff log group, profile snapshots and the reading category/sign/delivery route |
| Engagement | History/favorites, feedback, streaks, free stars, daily/weekly quests, qualified referrals, tarot collection and saved partner signs |
| Appearance | Friendly copy, configurable labels/welcome/footer, Telegram button styles and custom emoji fallback |
| Operations | Persistent queues, migrations, bounded reading history, online database backup, Docker/systemd and credential-free tests |

### Languages

The language picker intentionally starts with Chinese and Hindi:

| Order | Language | Code |
|---|---|---|
| 1 | 中文 — Simplified Chinese | `zh` |
| 2 | हिन्दी — Hindi | `hi` |
| 3 | فارسی — Persian | `fa` |
| 4 | العربية — Arabic | `ar` |
| 5 | English | `en` |
| 6 | Русский — Russian | `ru` |
| 7 | עברית — Hebrew | `he` |
| 8 | Español — Spanish | `es` |
| 9 | Français — French | `fr` |
| 10 | Türkçe — Turkish | `tr` |

Every new user chooses their language on the **first `/start`**, before the
main menu, membership prompt or readings. No interface language is selected
automatically from their Telegram locale. A saved choice is preserved on later
visits and can be changed with `/language`. Chinese and Hindi remain the first
two choices. The repository's primary README is English; the complete Persian
manual is [README.fa.md](README.fa.md).

All ten interface dictionaries are bundled. The administration panel is Persian.
The source readings are English; automatic reading translations require the
optional translation endpoint described below. Without it, the English source
is explicitly labelled in the user's interface language.

## Quick start

### 1. Requirements

- A Telegram bot token from [BotFather](https://t.me/BotFather).
- A Telegram API ID/hash from [my.telegram.org](https://my.telegram.org), also
  required when Telethon signs in as a bot.
- The numeric Telegram IDs of the administrators.
- A Linux server with Docker Compose, or Python 3.12 for direct execution.
- Outbound access to Telegram MTProto, `api.telegram.org` and the content API.

### 2. Configure

Clone the repository and enter its root:

```bash
git clone https://github.com/ByeCoder/Falino.git
cd Falino
```

Then create the local configuration:

```bash
cp .env.example .env
chmod 600 .env
```

Edit `.env` locally:

```dotenv
API_ID=123456
API_HASH=your_telegram_api_hash
BOT_TOKEN=123456789:your_bot_token
ADMIN_IDS=123456789
```

Separate multiple numeric administrator IDs with commas. Keep real credentials,
sessions and databases outside Git. `.env.example` contains empty placeholders.

### 3. Run

```bash
docker compose up -d --build
docker compose logs -f --tail=100
```

Open the bot's private chat, send `/start`, then use `/panel` as an administrator.
The first configured startup sets the Falino display name, localized descriptions
and command lists. No real Telegram credentials were supplied during development;
account-level sign-in and delivery must be verified with your own bot.

The Compose volume `astra-data` persists data across container replacement.
`docker compose down` keeps the volume; `docker compose down -v` deletes it.
Run one instance per token/data directory.

### Direct Python execution

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m astrobot
```

The original `astrobot` module, `astra.sqlite3` filename and deployment paths are
kept for upgrades from v1. The systemd example is in
[`deploy/astra.service`](deploy/astra.service); its default code path is
`/opt/astra_bot` and its data path is `/var/lib/astra`.

## Optional translation

Use a provider offering an OpenAI-compatible Chat Completions endpoint:

```dotenv
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=your_key
LLM_MODEL=your_available_model
```

These are placeholders, not a working service. The bot calls
`{LLM_BASE_URL}/chat/completions`. Public source reading text is translated and
cached across users; Telegram IDs and birth details are not sent for translation.
Provider costs may apply. Translation failure falls back to labelled source text.

Separate HTTP and Telethon proxy settings are documented in `.env.example`.

## Administration

### Staff groups

Add the bot as an administrator to a **private** group. Send `/chatid` there from
an account listed in `ADMIN_IDS`. Enter that negative ID under the appropriate
`/panel` setting:

- **Log group:** profile snapshots and reading activity.
- **Support group:** ticket cards and attachments; reply to the card to answer
  the user. Without this group, ticket notifications go to administrators' DMs.

Staff commands include `/reply 42 your answer`, `/ticket 42`, `/close 42` and
`!note internal text` when replying to a ticket message. Staff routes check the
configured group and the sender's numeric admin ID.

### Membership targets

Send the complete replacement channel list, one entry per line:

```text
@YourChannel | https://t.me/YourChannel
@YourOtherChannel | https://t.me/YourOtherChannel | members | 5000
-1001234567890 | https://t.me/+YourActualInvite | joins | 100
```

`members` means the total channel member count. `joins` counts an account only
when the bot first observed it as absent and later verified membership. Existing
members, repeated checks and profile recreation do not earn another credit.
Completed rules retire independently. `off` removes all required channels.

### Channel schedule

```text
@YourChannel | 6 | general | fa | all | 09:00 | Asia/Tehran
```

Fields: channel, interval in whole hours, content type, language, sign, first
wall-clock time, timezone. Types: `general`, `daily`, `weekly`, `monthly`, `yearly`,
`tarot`. Use `all` or a source zodiac identifier. The first send is at the next
occurrence of the selected time; later sends use a fixed hourly interval.

See the [Persian operating guide](README.fa.md) for all panel fields, target
semantics, rewards, message limits, backup/restore and troubleshooting context.

## User commands

| Purpose | Commands |
|---|---|
| Start and profile | `/start`, `/profile`, `/birthdate`, `/change_zodiac`, `/name`, `/language` |
| Readings | `/today`, `/weekly`, `/monthly`, `/yearly`, `/tarot`, `/spread`, `/natal`, `/moon`, `/compat` |
| Daily delivery | `/daily`, `/schedule`, `/stop` |
| Personal space | `/history`, `/favorites`, `/partners`, `/collection`, `/mood`, `/moods` |
| Engagement | `/streak`, `/rewards`, `/quests`, `/ref` |
| Support and data | `/support`, `/tickets`, `/faq`, `/privacy`, `/delete_me`, `/cancel` |

## Data and limits

- Administrators can see the profile fields available to the bot and data the
  user explicitly enters. The bot does not have access to phone numbers, IPs,
  contact lists or other private conversations.
- User-facing privacy notices explain local records, private staff logs,
  external birth-time calculations, deletion limits and keyed anti-abuse receipts.
- Local data is not application-level encrypted. Protect the server, staff groups
  and backups. Profile deletion cascades through personal local records and queues
  best-effort deletion of tracked staff copies; it cannot erase copies controlled
  by others or old backups.
- Anonymous daily aggregates and keyed duplicate-credit fingerprints remain after
  profile deletion. Precise event records are retained for 90 days.
- Reading history retains the latest 30 entries plus up to 20 favorites per user.
- Free stars are internal points without cash value. Payments, Telegram Stars
  billing and paid subscriptions are not implemented.

### Source coverage

[FreeHoroscopeAPI](https://freehoroscopeapi.com/) supplies current daily, weekly
and monthly written readings. It has no written annual endpoint or arbitrary
past/future-date selector. Annual content must be entered by an editor for each
year/sign/language. Same-sign users receive the same source reading; this is not
a unique birth-year-based daily prediction.

Provider date labels are preserved; source freshness is not guaranteed. A weekly
upstream outage was observed during verification and is handled independently.
Planetary positions do not include Ascendant, houses or a full chart
interpretation. Moon phase and zodiac-element comparisons are labelled as
approximate or playful. Content is for entertainment.

## Development

```bash
python -m pip install -r requirements-dev.txt
ruff check astrobot tests backup.py smoke_api.py benchmark.py
python -m compileall -q astrobot
python -m pytest -q
```

GitHub Actions runs these checks and builds the Docker image without production
credentials. Optional live source checks and a local-only benchmark:

```bash
python smoke_api.py
python benchmark.py --users 1000
```

`smoke_api.py` exits nonzero if any external endpoint fails. The benchmark excludes
Telegram, network, translation and log-group delivery; it is not a production
capacity promise. Current validation and known unverified areas are recorded in
[VALIDATION.md](VALIDATION.md).

## Project layout

| Module | Responsibility |
|---|---|
| `astrobot/core.py` | Configuration, calendar conversion and zodiac helpers |
| `astrobot/db.py`, `migrations.py` | Persistent state, transactions and upgrades |
| `astrobot/i18n.py`, `locales_extra.py` | Ten bundled locales |
| `astrobot/services.py` | Content API, translation, outbound Telegram and membership goals |
| `astrobot/app.py` | User routes and administration |
| `astrobot/analytics.py` | Calendar statistics and profile snapshots |
| `astrobot/support.py` | Tickets, staff replies and persistent outbox |
| `astrobot/experience.py` | History, rewards, referrals and engagement |
| `astrobot/scheduler.py` | Delivery workers and recovery |
| `astrobot/metadata.py` | Default/public and chat-specific Telegram command metadata |
| `astrobot/__main__.py` | Telethon lifecycle |

Read [CONTRIBUTING.md](CONTRIBUTING.md) to contribute and
[SECURITY.md](SECURITY.md) for sensitive reports. Release notes are in
[CHANGELOG.md](CHANGELOG.md).

## License and credits

**Copyright © 2026 Pouya Poorrahman and Falino contributors.**

Falino's original code, documentation and bundled artwork are licensed under the
[MIT License](LICENSE). Third-party dependencies and external content keep their
own licenses/terms; see [NOTICE.md](NOTICE.md) and [REFERENCES.md](REFERENCES.md).

**Powered by [FreeHoroscopeAPI](https://freehoroscopeapi.com/).** Keep the visible
source attribution in your deployment.
