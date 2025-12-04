# token_manager.py
import requests
from datetime import datetime, timedelta

class TokenManager:
    """
    Uses DB to fetch refresh token and persists access token and expiry.
    """
    def __init__(self, config, db: 'DB', service_name: str = "zoho_bigin"):
        self.config = config
        self.db = db
        self.service = service_name

        row = self.db.get_token_row(self.service)
        self.access_token = row["access_token"] if row else config.ACCESS_TOKEN
        self.refresh_token = row["refresh_token"] if row else config.REFRESH_TOKEN
        self.token_expiry = row["expires_at"] if row and row["expires_at"] else None

    def get_valid_token(self) -> str:
        if not self.refresh_token:
            return self.access_token

        if self.token_expiry:
            if isinstance(self.token_expiry, str):
                try:
                    self.token_expiry = datetime.fromisoformat(self.token_expiry)
                except:
                    self.token_expiry = None

        if self.token_expiry is None or datetime.utcnow() >= (self.token_expiry - timedelta(minutes=5)):
            refreshed = self._refresh_access_token()
            if not refreshed:
                return self.access_token
        return self.access_token

    def _refresh_access_token(self) -> bool:
        try:
            params = {
                'refresh_token': self.refresh_token,
                'client_id': self.config.CLIENT_ID,
                'client_secret': self.config.CLIENT_SECRET,
                'grant_type': 'refresh_token'
            }
            resp = requests.post(self.config.TOKEN_URL, params=params, timeout=15)
            if resp.status_code != 200:
                print(f"    ⚠ Token refresh failed: {resp.status_code} - {resp.text[:200]}")
                return False

            data = resp.json()
            self.access_token = data.get("access_token")
            expires_in = int(data.get("expires_in", 3600))
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

            new_refresh = data.get("refresh_token", None)
            if new_refresh:
                self.refresh_token = new_refresh

            self.db.upsert_token(
                service=self.service,
                access_token=self.access_token,
                refresh_token=self.refresh_token,
                expires_at=self.token_expiry.isoformat()
            )
            return True

        except Exception as e:
            print(f"    ⚠ Exception refreshing token: {e}")
            return False
