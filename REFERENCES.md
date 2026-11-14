# Reference review and implementation notes

Reviewed 2026-11-14. Repository README claims describe those projects; they do not establish that every third-party feature is operational today. This project is a new implementation. No source files from the repositories below were copied or bundled. They informed the feature selection and workflows. Their authors retain rights to their own code.

| Requested repository | What was inspected | Ideas incorporated in Astra | Boundaries |
|---|---|---|---|
| [king-tri-ton/DHoroBot](https://github.com/king-tri-ton/DHoroBot) | `readme.md`, SHA `2dcc0b13daa3f8612aef60ee2ec5b05ccf3c87ef` | Profile/birth-date editing, zodiac buttons, SQLite persistence, admin statistics | No Mail.ru scraping, group/forum handling, or AI chat. Original advertises MIT; no original code copied. |
| [ashutoshkrris/Telegram-Horoscope-Bot](https://github.com/ashutoshkrris/Telegram-Horoscope-Bot) | `bot.py` SHA `c22ed41f878e701ed455f774e73eba2042ddc214`; `utils.py` SHA `8526f88cfe812b1f0d5f93f0332112346abd25b0` | Sign selection followed by a reading; external JSON provider | The referenced older provider accepts day selectors; FreeHoroscopeAPI does not. No unsupported yesterday/tomorrow selector is exposed. |
| [JuliSem/horoscope_bot](https://github.com/JuliSem/horoscope_bot) | `README.md`, SHA `c826917be90b58949160bd80f279123a191b384d` | Zodiac menu, refresh/retrieve action, changing sign, timed daily delivery and ordinary duplicate suppression | Refresh fetches the current cached provider reading; it does not fabricate a different forecast. No bulk deletion of chat history or zodiac image pack. |
| [Kywas/astro-telegram-bot](https://github.com/Kywas/astro-telegram-bot) | `README.md`, SHA `04ad6b34e1ce074d3e6230711a0082046872d4d5` | Opt-in delivery, localization, mood journal, referral/source tracking, sharing, sign comparison, admin stats/broadcast, planetary birth snapshot and approximate moon phase | Full synastry, saved partner profiles, full natal chart, lunar reminders, paid Premium, Stars/fiat billing, trials and paid-Premium referral rewards are not implemented. v2 adds free in-bot referral points. Emoji Premium is a Telegram rendering permission, distinct from commercial memberships. |
| [modos/telegram-bot-daily-horoscope](https://github.com/modos/telegram-bot-daily-horoscope) | `app.js`, SHA `c1af57a3dfcc769560708bebb81fe518cc3ddb1e` | Multi-sign channel digest and a shared content-fetching layer | Its Puppeteer/Beytoote scraping is not used. Astra uses the requested JSON API to keep memory and maintenance requirements lower. |

## Official service contracts

- [FreeHoroscopeAPI docs](https://www.freehoroscopeapi.com/docs)
- [OpenAPI JSON](https://www.freehoroscopeapi.com/openapi.json)
- [API usage terms](https://freehoroscopeapi.com/terms)
- [Telethon bot sign-in](https://docs.telethon.dev/en/stable/basic/signing-in.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)

The provider supports only `daily`, `weekly`, and `monthly` written horoscope periods. API data is wrapped in `data` with `sign`, `period`, `date`, and `horoscope`. Tarot uses top-level `cards`/`nhits`. Calculated planetary positions use top-level `bodies`. Date freshness is not guaranteed by the provider. Astra preserves the date labels.

Button styles are limited to Telegram's `primary`, `success`, `danger`, or the default. Custom emoji rendering is permission-dependent and may differ in channels. The bot's use of both Telethon and outbound HTTP does not run two update pollers: all inbound events are Telethon-only.


## Additional v2 research

Reviewed primary project documentation and bot descriptions on 2026-11-14. These informed independent implementations; no source code was imported. Third-party account behaviour was not tested by logging into those bots.

| Source | Useful pattern | Implementation in Falino | Scope kept explicit |
|---|---|---|---|
| [bostrot/telegram-support-bot](https://github.com/bostrot/telegram-support-bot) | Reply routing, attachments, open/closed support and internal notes | SQLite-backed two-way tickets, configured private staff group, authenticated replies, attachments copied by Telegram, owner-only ticket viewing, internal notes, persistent outbox | No code from its GPL project is copied; no Signal bridge, AI agent, REST integration or per-ticket forum topic |
| [Daily Tarot / DailyTarotGroupBot](https://addthisbot.com/bots/tarot/) | Daily habit, streaks and a three-card spread | Daily tarot cache, streaks, past/present/future cards, collection and opt-in delivery | Falino stars are free points, not Telegram Stars or paid entitlements |
| [qilaidev/fortune-telling-bot](https://github.com/qilaidev/fortune-telling-bot) | The indexed README described multiple languages, reading history and multiple tarot spreads | Chinese interface first, ten-language UI, bounded reading history and a three-card provider spread | The page was readable during the initial review; a later fetch returned 404. No BaZi/I Ching/Zi Wei engine or code from that repository is bundled |

The five repositories originally supplied by the user remain the base reference set above. v2 adds qualified referral rewards, saved partner signs, birthday delivery, campaign counters and a mood/read daily quest. It does not copy another bot's branding, its user database, its private content or proprietary assets.

## Statistics and membership goals

Calendar statistics are a first-party implementation: Tehran local days, Saturday-start weeks and Jalali months. Source reading activity before v2 is not reconstructed. Targeted channel membership is independently implemented using Telegram membership checks and member counts; it does not assume an invite-link click is a verified join. Keyed duplicate-credit receipts prevent repeated acquisition/reward credit after a local profile is deleted and recreated.
