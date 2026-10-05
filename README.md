# Watchtower

Watchtower is a local-first Python CLI that monitors web pages and tells you when meaningful text changes. It supports whole-page monitoring, CSS selectors, readable diffs, SQLite history, scheduled checks, and terminal/Discord/Slack/Telegram/email notifications.

## Why

Use it for job pages, application deadlines, documentation, event pages, inventory pages, government notices, or any public page whose changes you do not want to check manually.

## Install

Python 3.10+ is required.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e .
watchtower init
```

For development:

```bash
pip install -e '.[dev]'
pytest
ruff check src tests
```

## Quick start

```bash
watchtower add https://example.com --name Example --interval 30
watchtower check 1       # first check creates the baseline
watchtower list
watchtower check 1       # later checks compare against the baseline
watchtower history 1
watchtower diff CHANGE_ID
watchtower run           # continuously check due monitors
```

Monitor one part of a page:

```bash
watchtower add https://example.com/jobs --name Jobs --selector '.jobs-list' --interval 15
```

Other commands:

```bash
watchtower disable 1
watchtower enable 1
watchtower remove 1
watchtower test-notification
```

## How it works

1. Fetch the page with redirects enabled and bounded retries.
2. Remove scripts/styles and normalize visible text.
3. Optionally restrict extraction to a CSS selector.
4. SHA-256 the normalized text.
5. Compare it with the latest stored version.
6. On change, create a unified diff, store history, and notify configured channels.

The first successful check is a baseline and does not trigger a change notification.

## Data and configuration

By default Watchtower stores its files in `~/.watchtower/`:

- `config.yml` — non-secret configuration
- `watchtower.db` — monitors, versions, and change history

Set `WATCHTOWER_HOME` to use a different directory.

## Discord

Edit `~/.watchtower/config.yml`:

```yaml
notifications:
  discord:
    enabled: true
    webhook_env: WATCHTOWER_DISCORD_WEBHOOK
```

Then set the secret in your shell rather than putting it in YAML:

```bash
export WATCHTOWER_DISCORD_WEBHOOK='your-webhook-value'
```

PowerShell:

```powershell
$env:WATCHTOWER_DISCORD_WEBHOOK='your-webhook-value'
```

## Slack and Telegram

Slack uses `WATCHTOWER_SLACK_WEBHOOK`. Telegram uses `WATCHTOWER_TELEGRAM_BOT_TOKEN` and `WATCHTOWER_TELEGRAM_CHAT_ID`. Enable the matching provider in `config.yml`; keep the actual secrets in environment variables.

## Email

Enable the email block in `config.yml`, then provide:

```text
WATCHTOWER_SMTP_HOST
WATCHTOWER_SMTP_PORT
WATCHTOWER_SMTP_USER
WATCHTOWER_SMTP_PASSWORD
WATCHTOWER_EMAIL_FROM
WATCHTOWER_EMAIL_TO
```

Credentials are deliberately read from environment variables and should never be committed.

## Scheduling

`watchtower run` stays active and checks each enabled monitor when its configured interval is due. For always-on use, run it under your operating system's process manager, Task Scheduler, cron, systemd, Docker, or another supervised environment.

## Dynamic sites and limitations

Watchtower fetches server-returned HTML. Pages whose important content exists only after JavaScript execution may require a browser-based renderer; that is intentionally not bundled because it greatly increases installation size and attack surface. CSS selectors are recommended for pages with frequently changing navigation, timestamps, ads, or unrelated content.

Respect site terms, robots guidance where applicable, authentication boundaries, and reasonable request intervals. Watchtower is not intended to bypass access controls, CAPTCHAs, or anti-bot systems.

## Architecture

```text
CLI / Scheduler
      |
      v
   Fetcher ---- HTTP
      |
      v
   Parser ---- CSS selector + normalization
      |
      v
 Change Engine ---- SHA-256 + unified diff
      |
      +---- SQLite versions/history
      |
      +---- Terminal / Discord / Slack / Telegram / Email
```

The modules are intentionally separated so additional fetchers or notification providers can be added without changing the monitoring engine.

## Testing

```bash
pytest --cov=watchtower
ruff check src tests
```

GitHub Actions runs linting and tests on supported Python versions.

## Security

- Notification secrets are environment variables, not database fields.
- No arbitrary page JavaScript is executed.
- Requests have timeouts and bounded retries.
- HTML is treated as data and converted to text.
- The SQLite database remains local unless you deliberately sync it elsewhere.

## License

MIT. See `LICENSE`.
