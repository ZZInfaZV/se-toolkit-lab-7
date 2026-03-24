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

    async def get_items(self) -> dict:
        """Get all items (labs and tasks) from the backend.

        Returns:
            Dict with 'items' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/items/")
            response.raise_for_status()
            items = response.json()
            return {"items": items}
        except httpx.TimeoutException:
            return {"error": "timeout (backend took too long)"}
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_learners(self) -> dict:
        """Get all enrolled learners from the backend.

        Returns:
            Dict with 'learners' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/learners/")
            response.raise_for_status()
            learners = response.json()
            return {"learners": learners}
        except httpx.TimeoutException:
            return {"error": "timeout (backend took too long)"}
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_scores(self, lab: str) -> dict:
        """Get score distribution for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            Dict with 'scores' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/analytics/scores", params={"lab": lab})
            response.raise_for_status()
            data = response.json()
            return {"scores": data}
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

    async def get_timeline(self, lab: str) -> dict:
        """Get submission timeline for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            Dict with 'timeline' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/analytics/timeline", params={"lab": lab})
            response.raise_for_status()
            data = response.json()
            return {"timeline": data}
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

    async def get_groups(self, lab: str) -> dict:
        """Get per-group scores for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            Dict with 'groups' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/analytics/groups", params={"lab": lab})
            response.raise_for_status()
            data = response.json()
            return {"groups": data}
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

    async def get_top_learners(self, lab: str, limit: int = 5) -> dict:
        """Get top learners for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").
            limit: Number of top learners to return.

        Returns:
            Dict with 'top_learners' list or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/analytics/top-learners", params={"lab": lab, "limit": limit})
            response.raise_for_status()
            data = response.json()
            return {"top_learners": data}
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

    async def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            Dict with 'completion_rate' value or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.get("/analytics/completion-rate", params={"lab": lab})
            response.raise_for_status()
            data = response.json()
            return {"completion_rate": data}
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

    async def trigger_sync(self) -> dict:
        """Trigger a data sync from the autochecker.

        Returns:
            Dict with sync result or 'error'.
        """
        try:
            client = await self._get_client()
            response = await client.post("/pipeline/sync")
            response.raise_for_status()
            data = response.json()
            return {"sync_result": data}
        except httpx.TimeoutException:
            return {"error": "timeout (backend took too long)"}
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except Exception as e:
            return {"error": str(e)}
