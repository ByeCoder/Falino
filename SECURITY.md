# Security policy

## Supported version

The current 2.x source release is maintained. Use the most recent published
2.x revision and a supported Python 3.12 patch release.

## Reporting a vulnerability

Use the repository's **Security → Report a vulnerability** option if the owner
has enabled private vulnerability reporting. Otherwise, contact the maintainer
through an existing private channel and share only a short, non-sensitive
summary until a private reporting channel is agreed. Do not post exploit details,
credentials, personal records or live support/audit messages in a public issue.

Provide the affected revision, a minimal reproduction with synthetic accounts,
expected behaviour, observed behaviour and the potential impact.
No response-time commitment is implied by this document.

## Deployment notes

- Keep `.env`, API hashes, bot tokens, session files and databases private.
- Only numeric IDs in `ADMIN_IDS` can use administrative and staff reply routes.
- Configure private staff/log groups and review who can read them.
- Use persistent, access-controlled storage and keep backups separately.
- The bot's own database is not application-level encrypted.
- Source providers and translation services are external dependencies.
- Profile deletion cannot guarantee erasure of old backups or copies controlled
  by other Telegram users. The user-facing privacy text describes these limits.

If a secret is exposed, revoke or rotate it at its issuing service rather than
only deleting the visible file from Git. Telegram session files need separate
handling from a bot token; see the installation guide.
