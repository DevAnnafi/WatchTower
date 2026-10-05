# Contributing to WatchTower

Thanks for considering a contribution.

## Development setup

1. Fork the repository and create a focused branch.
2. Create and activate a Python 3.10+ virtual environment.
3. Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

4. Make a focused change and add or update tests.
5. Run the quality gate:

```bash
python -m ruff check src tests
python -m pytest
python -m pytest --cov=watchtower --cov-report=term-missing
```

6. Open a pull request explaining the behavior change and how it was tested.

## Guidelines

- Keep changes focused and backwards-compatible when practical.
- Prefer small modules and explicit error handling.
- Add tests for bug fixes and new behavior.
- Do not commit `.env` files, API keys, SMTP passwords, bot tokens, or webhook URLs.
- Do not add functionality intended to bypass authentication, CAPTCHAs, access controls, or anti-bot protections.
