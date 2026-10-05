# Changelog

All notable changes to WatchTower are documented here.

## 1.0.1 - 2026-10-05

- Added Python 3.14 to the GitHub Actions CI matrix.
- Cleaned up lint and import-order issues.
- Restored scheduler polling delay behavior.
- Added explicit SQLite commit, rollback, and connection cleanup.
- Eliminated unclosed SQLite connection warnings under Python 3.14.
- Verified 7/7 automated tests on Windows with Python 3.14.7.
- Verified end-to-end local change detection and Discord webhook delivery.

## 1.0.0 - 2026-10-05

- Added website monitoring with normalized text extraction.
- Added whole-page and CSS-selector monitoring.
- Added SHA-256 change detection and unified diffs.
- Added SQLite history and version storage.
- Added CLI management and continuous scheduling.
- Added terminal, Discord, Slack, Telegram, and SMTP email notifications.
- Added YAML configuration with secrets supplied through environment variables.
- Added tests, CI, packaging, Docker support, and documentation.
