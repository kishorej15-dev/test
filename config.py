# config.py
import os
from datetime import datetime

class Config:
    # -------------------------
    # OAuth / Zoho settings
    # -------------------------
    CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "1000.GXPK7PLQD9SPH5G1MX6XB1Y3QBTXXN")
    CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "26832a9fc42886a569e9e41f5fce59d059375a3ae5")
    BASE_URL = os.getenv("ZOHO_BASE_URL", "https://www.zohoapis.in/bigin/v2")
    TOKEN_URL = os.getenv("ZOHO_TOKEN_URL", "https://accounts.zoho.in/oauth/v2/token")

    # --- Tokens placed per your request (for local/testing). 
    # SECURITY: Do NOT commit this file with real tokens to public repos.
    ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN", "1000.addac49da6a97d98e9fd4deb02d9b99e.430658aa62b2b0aefd17b7d84ae41bd0")
    REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "1000.7be79d01ac54e88968827f579ec67881.b6af36cbff584305820f52b5772f311b")

    # Informational scope string (not used programmatically)
    OAUTH_SCOPES = os.getenv("ZOHO_OAUTH_SCOPES", "ZohoBigin.settings.ALL,ZohoBigin.modules.contacts.ALL,ZohoBigin.modules.accounts.READ,ZohoBigin.bulk.READ,ZohoBigin.bulk.ALL,ZohoBigin.modules.deals.READ,ZohoBigin.modules.ALL,ZohoBigin.modules.pipelines.ALL,ZohoBigin.modules.events.READ")

    # Modules to fetch
    MODULES_TO_FETCH = [
        "Contacts", "Accounts", "Pipelines", "Calls", "Events", "Tasks", "Notes"
    ]

    # Date range (default: current month)
    MONTH_START = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    MONTH_END = datetime.now()

    # API / request parameters
    RECORDS_PER_PAGE = int(os.getenv("ZOHO_RECORDS_PER_PAGE", 200))
    MAX_RETRIES = int(os.getenv("ZOHO_MAX_RETRIES", 3))
    REQUEST_TIMEOUT = int(os.getenv("ZOHO_REQUEST_TIMEOUT", 30))
    RATE_LIMIT_DELAY = float(os.getenv("ZOHO_RATE_LIMIT_DELAY", 0.5))

    # Database (SQL Server) ODBC string - set as env var for production
    SQL_ODBC = os.getenv("SQL_SERVER_ODBC", "")
