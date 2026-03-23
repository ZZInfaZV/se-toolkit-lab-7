"""LMS API client.

Async HTTP client for the LMS backend with Bearer token authentication.
"""

import httpx

from config import load_config


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self) -> None:
        """Initialize the LMS client."""
        config = load_config()
        self.base_url = config["LMS_API_URL"].rstrip("/")
        self.api_key = config["LMS_API_KEY"]
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client.

        Returns:
            Configured httpx.AsyncClient with auth headers.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_health(self) -> dict:
        """Check backend health by fetching items count.

        Returns:
            Dict with 'healthy' status and 'item_count' or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/items/")
            response.raise_for_status()
            items = response.json()
            return {"healthy": True, "item_count": len(items)}
        except httpx.TimeoutException:
            return {"healthy": False, "error": "timeout (backend took too long)"}
        except httpx.ConnectError as e:
            return {"healthy": False, "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"healthy": False, "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def get_labs(self) -> dict:
        """Get all labs from the backend.

        Returns:
            Dict with 'labs' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/items/")
            response.raise_for_status()
            items = response.json()
            labs = [item for item in items if item.get("type") == "lab"]
            return {"labs": labs}
        except httpx.TimeoutException:
            return {"error": "timeout (backend took too long)"}
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_pass_rates(self, lab: str) -> dict:
        """Get pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            Dict with 'pass_rates' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            data = response.json()
            return {"pass_rates": data}
        except httpx.TimeoutException:
            return {"error": "timeout (backend took too long)"}
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"lab '{lab}' not found"}
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"error": str(e)}
