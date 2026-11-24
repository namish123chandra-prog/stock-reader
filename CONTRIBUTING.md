# Contributing to Stock Buddy

Thanks for wanting to help. This project is for beginners, so the best
contributions are the ones that make the app **clearer**, **safer** and
**easier to understand**.

## Good first contributions

- Fix a confusing sentence or error message.
- Add an NSE company alias in `core/market.py` (for example, a nickname people
  actually use).
- Add a term to the glossary in `features/chat_help.py`.
- Add a unit test for an existing feature.
- Improve the README or screenshot.

## Adding a feature

1. Copy `features/_template.py` to `features/your_feature.py`.
2. Give it a unique `name`, optional `button`, and a sensible `priority`.
3. Implement `can_handle` and `handle`.
4. Use `app.notify(title, message)` if it should send an alert.
5. Add a test in `tests/` if the feature does not need the internet.
6. Restart the app and try both the button and the chat command.

Keep new features small and readable. Short comments are welcome. Clever
one-liners that a beginner cannot follow are not.

## Before opening a pull request

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
```

Both must pass.

## Never commit personal data

Do not commit any of these:

- API keys or bot tokens
- phone numbers
- `portfolio.json`
- `watchlist.json`
- `targets.json`
- `alerts_log.txt`
- `app.log`
- `backups/`
- screenshots that show personal information

They are already listed in `.gitignore`. If you accidentally commit a secret,
remove it and rotate the key immediately.

## Style

- Python 3.9+ compatible.
- Plain English in user-facing text.
- 4-space indentation.
- Keep features independent: one file should not need edits to another feature.
- No new dependency unless it is really necessary.

## Reporting bugs

Use the **Bug report** issue template. Include the exact text you typed, what
you expected, and what happened. Screenshots help, but remove personal data
first.

## Code of conduct

Be kind. This is a learning project, and many contributors will be students.
No mocking, harassment or gatekeeping. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
