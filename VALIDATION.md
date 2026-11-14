# Falino v2 validation record

Date: 2026-11-14 (Asia/Tehran)

## Automated checks

- **72 automated tests passed** on Python 3.12 (including first-start language selection).
- Ruff passed for all application modules, tests, backup, live smoke script and benchmark.
- Every application module compiled successfully.
- All ten locales have **101 matching bundled keys**; fixed UI key usage was checked against the dictionary.
- Menu/extra-menu/privacy screens were checked for Telegram text/button/callback limits across all ten languages.
- Startup without secrets exits clearly and names the four required variables.
- The avatar was rendered from the bundled SVG to an 800 × 800 PNG and visually inspected.

Coverage includes the original v1 flows plus:

- Tehran day boundaries, Saturday weeks and Jalali-month starts;
- distinct active users and successful-reading counts, period filtering, and failure exclusion;
- idempotent schema upgrade preserving v1 users and registration totals;
- two-way support, unauthorized reply rejection, user ownership, closed tickets, private inbox and attachment copying;
- panel replies with attachments, internal notes never delivered to users, and per-user support limits;
- profile snapshots and reading types in the durable audit queue;
- personal-data cascades, queued staff-copy deletion and stale history isolation;
- daily/quest reward idempotence and referral qualification;
- duplicate referral/acquisition prevention across deletion and recreation;
- bounded history, favorites and pagination;
- total-members target completion, verified-new-join attribution, duplicate checks, pre-existing-member exclusion and counter outages;
- blocked/banned delivery behaviour, including preventing banned accounts from starving a due delivery batch;
- persistent scheduler worker registration and shutdown;
- birth-calendar anniversary handling and three distinct provider tarot cards.

## Live source API

Verified with the supplied `smoke_api.py`, without Telegram credentials:

| Endpoint | Result |
|---|---|
| Daily horoscope | OK; provider date 2026-11-14 |
| Weekly horoscope | Unavailable after bounded retries; an earlier direct check returned HTTP 504 upstream_timeout |
| Monthly horoscope | OK; provider label 2026-11 |
| Daily tarot | OK |
| Three-card tarot | OK; three distinct cards and four formatted output messages including the explanation |
| Birth planetary positions | OK |

The live smoke exits nonzero if any endpoint is unavailable; that exit is recorded as a partial upstream outage, not a passing full API run. Endpoint circuit breakers are isolated so a weekly outage does not disable daily/monthly/tarot.

## Local resource sample

Command: `python benchmark.py --users 1000`

- 1,000 profiles plus 1,000 successful daily-reading handler flows;
- 14.61 seconds elapsed;
- 25.8 MiB peak process RSS on Linux;
- 4.88 MiB combined database/WAL/SHM at the measurement point.

**Scope:** this is a local-handler/SQLite sample, with fake send/content adapters. It excludes a live Telethon connection, network, translations, Telegram rate limits and audit-group delivery. It is not a production RAM or throughput guarantee. The benchmark uses a temporary database and makes no external calls.

## Not verified without the owner's environment

No real Telegram credentials, translation-service key or production server were supplied. Consequently:

- live Telethon sign-in and Bot API delivery;
- actual channel/group permissions and support reply routing on a Telegram account;
- premium/custom-emoji eligibility and rendering;
- model-provider translation quality;
- systemd installation and production capacity

remain to be checked after configuration. Docker is not installed in the build workspace. No token, API hash, user database or session file is included in the archive.


## Repository preparation — 2.0.1

- The full 60-test suite and Ruff/compilation checks passed again on 2026-11-14.
- The MIT license, English/Persian documentation, contribution/security guides,
  GitHub issue forms and workflow YAML were checked. Local Markdown links resolve.
- A pinned tzdata fallback was verified with `PYTHONTZPATH` empty, so the app can
  import and find Tehran/Shanghai/Kolkata zones without system timezone files.
- The CI definition has read-only repository permission, credential-free tests,
  Docker build and an isolated image-import/timezone check. The workflow has not
  been run on GitHub at this local preparation stage. Docker is unavailable here.
- The publication payload contains no real environment file, token, API hash,
  Telegram session, database or private support log.

## First-start language selection — 2.0.2

- New users must explicitly choose a language before opening menus or readings;
  Chinese and Hindi appear first. Telegram's interface language does not select
  or overwrite their choice. Existing saved language preferences are preserved.
- Tests cover six Telegram locale variants, saved choices, migration, privacy
  access before selection and localized per-chat command lists.
- The primary repository README is English, with a complete Persian README.
- The initial GitHub write was blocked until the owner installed ChatGPT Codex
  Connector for the repository account. Write access to `ByeCoder/Falino` was
  then verified by successfully publishing the MIT license on 2026-11-14.
- GitHub CI results are available in the repository Actions tab. Live Telegram
  deployment still requires the owner's credentials and server configuration.

## GitHub CI — 2026-11-14

Verified on commit `039006f0fb9ed1ad8c0b48d9f90b0b5481516dc1`:

- Python 3.12: dependency installation, Ruff, compilation and all 72 tests passed.
- Docker: image build passed; the built image imported the application and
  resolved `Asia/Tehran` successfully with network access disabled.
- All 47 published files match the prepared local Git tree.
- Evidence: https://github.com/ByeCoder/Falino/actions/runs/43556746707

These checks do not sign in to Telegram or deploy a live bot.
