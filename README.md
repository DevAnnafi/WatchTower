# WatchTower

[![CI](https://github.com/DevAnnafi/WatchTower/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/DevAnnafi/WatchTower/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/DevAnnafi/WatchTower)](https://github.com/DevAnnafi/WatchTower/releases)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

WatchTower is a local-first Python CLI that monitors public web pages and tells you when meaningful text changes. It supports whole-page monitoring, CSS selectors, readable diffs, SQLite history, scheduled checks, and terminal, Discord, Slack, Telegram, and SMTP email notifications.

## Why WatchTower?

Use it for job pages, application deadlines, documentation, event pages, inventory pages, government notices, release pages, or any public page you do not want to check manually.

WatchTower keeps monitoring data local by default and reads notification credentials from environment variables rather than storing secrets in its database.

## Features

- Whole-page and CSS-selector monitoring
- SHA-256 content fingerprints
- Human-readable unified diffs
- SQLite-backed version and change history
- Configurable monitor intervals
- Continuous scheduler
- HTTP redirects, timeouts, and bounded retries
- Terminal notifications
- Discord webhooks
- Slack webhooks
- Telegram bot notifications
- SMTP email notifications
- Environment-variable secret management
- Docker and Docker Compose support
- GitHub Actions CI across Python 3.10-3.14

## Architecture

```text
CLI / Scheduler
      |
      v
   Fetcher -------- HTTP
      |
      v
   Parser --------- CSS selector + text normalization
      |
      v
 Change Engine ---- SHA-256 + unified diff
      |
      +-----------> SQLite versions/history
      |
      +-----------> Terminal / Discord / Slack / Telegram / Email
```

The modules are intentionally separated so additional fetchers or notification providers can be added without changing the core monitoring engine.

## Installation

Python 3.10+ is required.

```bash
git clone https://github.com/DevAnnafi/WatchTower.git
cd WatchTower
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install WatchTower and initialize it:

```bash
python -m pip install -e .
watchtower init
```

## Quick start

Add a monitor:

```bash
watchtower add https://example.com --name "Example" --interval 30
```

Run the first check. The first successful check creates a baseline and does not send a change notification.

```bash
watchtower check 1
```

Later checks compare the current page against the latest stored version:

```bash
watchtower check 1
watchtower history 1
watchtower diff CHANGE_ID
```

Run WatchTower continuously:

```bash
watchtower run
```

## CSS selector monitoring

Monitor only one part of a page:

```bash
watchtower add https://example.com/jobs \
  --name "Jobs" \
  --selector ".jobs-list" \
  --interval 15
```

Selectors are useful when navigation, timestamps, advertisements, or unrelated page content change frequently.

## CLI commands

```text
watchtower init
watchtower add URL [--name NAME] [--selector SELECTOR] [--interval MINUTES]
watchtower list
watchtower check [MONITOR_ID]
watchtower history MONITOR_ID
watchtower diff CHANGE_ID
watchtower enable MONITOR_ID
watchtower disable MONITOR_ID
watchtower remove MONITOR_ID
watchtower run
watchtower test-notification
```

## Data and configuration

By default, WatchTower stores runtime files under `~/.watchtower/`:

```text
~/.watchtower/
├── config.yml
└── watchtower.db
```

Set `WATCHTOWER_HOME` to use another directory.

A complete non-secret configuration example is available at `examples/config.yml`.

## Discord

Enable Discord in `~/.watchtower/config.yml`:

```yaml
notifications:
  discord:
    enabled: true
    webhook_env: WATCHTOWER_DISCORD_WEBHOOK
```

Then set the webhook in your shell instead of placing it in YAML.

**PowerShell**

```powershell
$env:WATCHTOWER_DISCORD_WEBHOOK="your-webhook-value"
```

**macOS/Linux**

```bash
export WATCHTOWER_DISCORD_WEBHOOK="your-webhook-value"
```

Test the configured notification providers:

```bash
watchtower test-notification
```

## Slack and Telegram

Slack reads `WATCHTOWER_SLACK_WEBHOOK`.

Telegram reads:

```text
WATCHTOWER_TELEGRAM_BOT_TOKEN
WATCHTOWER_TELEGRAM_CHAT_ID
```

Enable the matching provider in `config.yml` and keep the actual credentials in environment variables.

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

## Docker

Build and run directly:

```bash
docker build -t watchtower .
docker run --rm -v watchtower-data:/data watchtower
```

Or use Docker Compose:

```bash
docker compose up -d
```

Runtime data is stored in the `/data` volume. Notification secrets can be supplied through a local `.env` file, which is ignored by Git.

## Scheduling

`watchtower run` remains active and scans enabled monitors every configured scheduler polling interval. A monitor is fetched only when its own interval is due.

For always-on use, run WatchTower under Task Scheduler, cron, systemd, Docker, or another supervised process environment.

## Dynamic sites and limitations

WatchTower fetches server-returned HTML. Content rendered only after JavaScript executes may require a browser-based renderer, which is intentionally not bundled into the current release.

WatchTower is designed for public pages. It is not intended to bypass authentication, CAPTCHAs, access controls, rate limits, or anti-bot protections. Use reasonable request intervals and respect applicable site terms and policies.

## Development

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the quality gate:

```bash
python -m ruff check src tests
python -m pytest
python -m pytest --cov=watchtower --cov-report=term-missing
```

The v1.0.1 release was manually validated on Windows with Python 3.14.7, including end-to-end page-change detection, SQLite history/diffs, scheduler startup, and Discord webhook delivery.

## Security

- Notification credentials are read from environment variables.
- `.env`, `.venv`, runtime data, caches, coverage files, and build artifacts are ignored by Git.
- HTML is treated as data; WatchTower does not execute page JavaScript.
- HTTP requests use timeouts and bounded retries.
- SQLite connections are explicitly committed/rolled back and closed.
- Runtime data remains local unless you deliberately sync or mount it elsewhere.

See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.

## Roadmap

Potential post-v1 improvements are tracked separately from the stable v1.0.1 release. Good candidates include higher automated coverage, browser-rendered pages, richer notification formatting, and additional scheduling/deployment options.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
