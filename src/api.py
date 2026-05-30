import httpx
from typing import Optional
import time

OPENROUTER_BASE = "https://openrouter.ai/api/v1"


class OpenRouterClient:
    def __init__(self, management_key: str, max_retries: int = 3):
        self._headers = {
            "Authorization": f"Bearer {management_key}",
            "Content-Type": "application/json",
        }
        self._max_retries = max_retries

    def _request_with_retry(self, method: str, url: str) -> dict:
        """Execute HTTP request with exponential backoff retry."""
        last_exc = None
        for attempt in range(self._max_retries):
            try:
                with httpx.Client(timeout=15) as client:
                    resp = client.request(method, url, headers=self._headers)
                    resp.raise_for_status()
                    return resp.json()
            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries - 1:
                    wait = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(wait)
        raise last_exc

    def get_keys(self) -> list[dict]:
        """Return all API keys with usage metrics."""
        data = self._request_with_retry("GET", f"{OPENROUTER_BASE}/keys")
        # API returns {"data": [...]}
        return data.get("data", data) if isinstance(data, dict) else data

    def get_credits(self) -> dict:
        """Return account-level credit info."""
        data = self._request_with_retry("GET", f"{OPENROUTER_BASE}/credits")
        # API returns {"data": {"total_credits": ..., "total_usage": ...}}
        return data.get("data", data) if isinstance(data, dict) and "data" in data else data

    def get_activity(self) -> list[dict]:
        """Return account-level activity grouped by model and date."""
        data = self._request_with_retry("GET", f"{OPENROUTER_BASE}/activity")
        return data.get("data", []) if isinstance(data, dict) else data
