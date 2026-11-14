# Falino 2.0

2026-11-14

- Rebranded the user-facing bot as **Falino | فالینو ✨**. Existing `astrobot` imports, the original database filename and deployment paths remain compatible.
- Expanded from four to ten bundled locales, with Chinese and Hindi first. Added Russian, Hebrew, Spanish and French, and retained Persian, Arabic, English and Turkish.
- Added calendar-period statistics, unique activity tracking, transactional daily aggregates and an admin user dossier/search.
- Added an authenticated two-way support desk, reply routing from private staff groups, attachments, ticket history, close controls and internal notes.
- Added configurable private audit logs with profile snapshots and reading classifications, backed by a persistent outbox.
- Added total-members and verified-new-joins targets for mandatory channels. Target completion retires only that channel's rule. Existing members and repeated checks do not generate acquisition credits.
- Added keyed duplicate-credit protection across profile deletion/recreation; anonymous counters and anti-abuse fingerprints are explained in all privacy locales.
- Added reading history/favorites, feedback, daily streaks, daily/weekly quests, free stars, qualified referral rewards, campaign links, saved partners, tarot collection, three-card tarot and birthday greetings within opted-in daily delivery.
- Added a database migration, bounded history, privacy-aware cascades, staff-copy deletion requests, safe shutdown for the outbox, an SVG brand asset and integration tests.

This release adds no payment processor, paid entitlement system, complete natal-chart/synastry engine or guaranteed exclusive brand/username. Source-provider coverage and availability remain external dependencies.

# Falino 2.0.1 — repository preparation

2026-11-14

- Added the full MIT license under Pouya Poorrahman and Falino contributors.
- Expanded the English README and added a Persian GitHub publication guide.
- Added attribution/dependency-license boundaries, contribution/security guides,
  issue forms, a pull request template, Git attributes and broader secret/data
  exclusions.
- Added a credential-free Python CI job and a Docker build job; no automatic
  deployment or production account action is configured.
- Existing bot behaviour and data paths remain unchanged.
- Added a pinned timezone-data fallback and a CI container import/timezone check
  for minimal Linux images without a system timezone database.


# Falino 2.0.2 — first-start language choice and GitHub publication

2026-11-14

- Require an explicit language selection on the first start before the main
  menu, membership prompts and readings. Chinese/Hindi stay first; returning
  users retain their saved language choice.
- Add a migration that marks existing valid language preferences as selected
  without assigning a default to new profiles.
- Set chat-specific command descriptions after a user chooses a language.
- Keep English as the repository's primary documentation, alongside the full
  Persian README, and add the official ByeCoder/Falino clone instructions.
- Centralize public/localized Telegram metadata and add onboarding coverage.
