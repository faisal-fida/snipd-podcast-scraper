import asyncio
import copy
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientResponseError, ClientTimeout, TCPConnector

from snipd_pipeline.config import (
    api_url,
    headers,
    json_data_shows,
    json_data_episodes,
    json_data_episode_by_id,
)


class SnipdAPI:
    def __init__(self) -> None:
        self.headers = headers
        self.api_url = api_url
        self._session: Optional[aiohttp.ClientSession] = None
        self._timeout = ClientTimeout(total=30)
        # Delay connector creation to async context to avoid no running loop error
        self._connector_args = {"limit": 100, "enable_cleanup_closed": True}
        self._connector = None

    async def __aenter__(self) -> "SnipdAPI":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _ensure_session(self) -> None:
        if self._session is None:
            # Instantiate connector within running event loop
            connector = TCPConnector(**self._connector_args)
            self._session = aiohttp.ClientSession(
                timeout=self._timeout, connector=connector
            )

    async def close(self) -> None:
        """Public close method to explicitly close the underlying session."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _post(self, json_payload: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_session()
        assert self._session is not None

        url = f"{self.api_url}/public/graphql"
        attempt = 0
        last_exc: Optional[Exception] = None
        while attempt < 5:
            try:
                async with self._session.post(
                    url,
                    headers=self.headers,
                    json=json_payload,
                ) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            except (
                aiohttp.ClientError,
                ClientResponseError,
                asyncio.TimeoutError,
            ) as exc:  # noqa: TRY003
                last_exc = exc
                attempt += 1
                base = 0.5
                cap = 8.0
                import logging as _log

                _log.warning(f"HTTP error on attempt {attempt}: {exc}")
                # Jittered exponential backoff
                import random as _r

                backoff = min(cap, base * (2 ** (attempt - 1)))
                jitter = _r.uniform(0, backoff / 2)
                await asyncio.sleep(backoff + jitter)
        assert last_exc is not None
        raise last_exc

    async def get_top_shows(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Get top podcast shows from Snipd API
        """
        payload = copy.deepcopy(json_data_shows)
        payload["variables"]["limit"] = limit
        payload["variables"]["offset"] = offset
        response_json = await self._post(payload)
        return response_json["data"]["top_listened_shows"]

    async def get_episodes(
        self, show_id: str, limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """
        Get episodes for a podcast show from Snipd API
        """
        payload = copy.deepcopy(json_data_episodes)
        payload["variables"]["id"] = show_id
        payload["variables"]["limit"] = limit
        payload["variables"]["offset"] = offset
        response_json = await self._post(payload)
        return response_json["data"]["episodes"]

    async def get_episode_by_id(self, episode_id: str) -> Dict[str, Any]:
        """
        Get episode by id from Snipd API
        """
        payload = copy.deepcopy(json_data_episode_by_id)
        payload["variables"]["id"] = episode_id
        response_json = await self._post(payload)
        return response_json["data"]["episode"]
