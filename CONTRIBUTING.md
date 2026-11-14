# Contributing to Falino

Thanks for helping make Falino useful, friendly and reliable.

## Development setup

Use Python 3.12 on Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

The unit/integration suite runs without a bot token, Telegram login or translation
key. Use fake adapters for new tests; keep network-dependent source checks in
`smoke_api.py`.

```bash
ruff check astrobot tests backup.py smoke_api.py benchmark.py
python -m compileall -q astrobot
python -m pytest -q
```

## Changes and pull requests

1. Open an issue for a substantial feature or behavioural change.
2. Work on a focused branch and describe the user-visible result.
3. Add meaningful regression coverage for behaviour, ownership, timing or delivery
   changes. Small documentation and cosmetic edits do not need artificial tests.
4. Update the relevant README and `CHANGELOG.md` when behaviour changes.
5. Run the checks above and include the result in the pull request.

GitHub Actions repeats Python checks and builds the Docker image. It deliberately
does not run live Telegram operations or make a flaky upstream service a required
CI dependency.

## Translations

Locale dictionaries live in `astrobot/i18n.py` and `astrobot/locales_extra.py`.
Keep key parity across the ten locales and preserve template fields such as
`{id}` and `{name}`. Chinese (`zh`) and Hindi (`hi`) stay first in the language
picker. Persian administration texts are separate from user-interface locales.

## Database changes

Add idempotent, forward-compatible migrations in `astrobot/migrations.py`.
Preserve existing user data and test upgrading an old schema. Keep local data
and real backups out of commits.

## Reporting problems

Use the repository's Issues tab for reproducible bugs and feature suggestions.
Provide Python/OS versions, reproduction steps and redacted error output.
Never attach a real `.env`, bot token, API hash, session, user database, support
transcript or identifiable audit-group screenshot.

For security-sensitive reports, follow [SECURITY.md](SECURITY.md).

## License

Contributions are submitted under the project's [MIT License](LICENSE).
Do not introduce third-party source without checking its license and preserving
any required notices. [NOTICE.md](NOTICE.md) explains external content and
package attribution.
