# Zoho Bigin Analytics - Modular

## What you received
- A modular Python project that fetches Zoho Bigin data, calculates metrics, and exports an Excel report.
- Tokens provided in `config.py` per your request (for local/testing). Consider using env vars or a secrets manager.

## Quick steps
1. Install requirements:
   ```
   pip install -r requirements.txt
   ```
2. Create the `zoho_tokens` table in your SQL Server (example in earlier chat).
3. Set `SQL_SERVER_ODBC` environment variable with your ODBC connection string, or edit `config.py` temporarily.
4. Ensure `zoho_tokens` has a row for `service='zoho_bigin'` with a refresh token.
5. Run:
   ```
   python main.py
   ```

## Security note
Do not commit `config.py` with real tokens to public repositories.


## Secrets
Fill `secrets.env` with your SQL Server ODBC connection string (see the file). Do not commit that file.
