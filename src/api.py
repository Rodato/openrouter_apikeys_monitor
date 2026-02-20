import httpx
from typing import Optional

OPENROUTER_BASE = "https://openrouter.ai/api/v1"


class OpenRouterClient:
    def __init__(self, management_key: str):
        self._headers = {
            "Authorization": f"Bearer {management_key}",
            "Content-Type": "application/json",
        }

    def get_keys(self) -> list[dict]:
        """Return all API keys with usage metrics."""
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{OPENROUTER_BASE}/keys", headers=self._headers)
            resp.raise_for_status()
            data = resp.json()
            # API returns {"data": [...]}
            return data.get("data", data) if isinstance(data, dict) else data

    def get_credits(self) -> dict:
        """Return account-level credit info."""
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{OPENROUTER_BASE}/credits", headers=self._headers)
            resp.raise_for_status()
            return resp.json()
