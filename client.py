# client.py
import requests
import time
from typing import List, Dict, Optional, Tuple

class ZohoBiginClient:
    def __init__(self, token_manager, base_url, config):
        self.token_manager = token_manager
        self.base_url = base_url
        self.config = config
        self.session = requests.Session()

    def _get_headers(self):
        token = self.token_manager.get_valid_token()
        if not token:
            raise RuntimeError("No access token available")
        return {"Authorization": f"Zoho-oauthtoken {token}", "Content-Type": "application/json"}

    def _fetch_page(self, module_name: str, page: int, fields: Optional[str] = None) -> Tuple[bool, List[Dict], bool]:
        api_url = f"{self.base_url}/{module_name}"
        params = {"page": page, "per_page": self.config.RECORDS_PER_PAGE}
        if fields:
            params["fields"] = fields

        for attempt in range(self.config.MAX_RETRIES):
            try:
                resp = self.session.get(api_url, params=params, headers=self._get_headers(), timeout=self.config.REQUEST_TIMEOUT)
                if resp.status_code == 200:
                    j = resp.json()
                    return True, j.get("data", []), j.get("info", {}).get("more_records", False)
                elif resp.status_code == 401:
                    print("    ⚠ 401 - refreshing token and retrying")
                    self.token_manager._refresh_access_token()
                    continue
                elif resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 60))
                    print(f"    ⚠ Rate limit - waiting {wait}s")
                    time.sleep(wait)
                    continue
                elif resp.status_code == 204:
                    return True, [], False
                else:
                    print(f"    ⚠ HTTP {resp.status_code}: {resp.text[:200]}")
                    time.sleep(2 ** attempt)
                    continue
            except requests.exceptions.Timeout:
                print(f"    ⚠ Timeout (attempt {attempt + 1})")
                time.sleep(2)
                continue
            except requests.exceptions.RequestException as e:
                print(f"    ⚠ Request exception: {e}")
                time.sleep(2)
                continue
        return False, [], False

    def _get_module_fields(self, module_name: str) -> Optional[str]:
        try:
            url = f"{self.base_url}/settings/fields"
            resp = self.session.get(url, params={"module": module_name}, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                fields = resp.json().get("fields", [])
                names = [f.get("api_name") for f in fields if f.get("api_name")]
                return ",".join(names) if names else None
        except Exception:
            pass
        return None

    def fetch_module_data(self, module_name: str) -> List[Dict]:
        all_records = []
        page = 1
        print(f"  📥 Fetching {module_name}...", end=" ", flush=True)

        fields = self._get_module_fields(module_name)

        while True:
            ok, records, has_more = self._fetch_page(module_name, page, fields)
            if not ok:
                if page == 1:
                    print("❌ Failed")
                    return []
                break
            if records:
                all_records.extend(records)
            if not has_more:
                break
            page += 1
            time.sleep(self.config.RATE_LIMIT_DELAY)

        print(f"✓ {len(all_records)} records")
        return all_records
