# Security policy

## Supported versions

Only the latest release (currently **v1.2.x**) receives security fixes.

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

1. Go to the repository's **Security** tab.
2. Choose **Report a vulnerability** (private advisory).
3. Describe the problem and how to reproduce it.

Link: <https://github.com/namish123chandra-prog/stock-reader/security/advisories/new>

If private reporting is unavailable, open a normal issue that says only
"security issue - please contact me", without exploit details or secrets.

## Secrets

Stock Buddy reads optional keys from `config.py`:

- `SMS_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `TELEGRAM_BOT_TOKEN`

They are **blank by default**. Never commit real keys or a real phone number.
If a key is exposed:

1. Revoke it in the provider's dashboard.
2. Create a new key.
3. Remove the old value from git history before publishing again.

## What this app does not do

- It does not ask for a broker login or password.
- It does not place trades.
- It does not store payment information.
- It does not send your portfolio anywhere except the price/news providers it
  queries (Yahoo Finance and public RSS feeds).
