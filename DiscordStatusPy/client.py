"""
Sub-module with the client implementation
"""

from __future__ import annotations

import asyncio
import atexit
from types import TracebackType
from typing import (
    ClassVar,
    Optional,
    Type
)


from aiohttp import ClientSession, ClientError


from .urls import *


JSONResponce = Optional[dict[str, "JSONResponce"]]


class APIClient():
    """
    Class to represent a client connection
    """
    session_map: ClassVar[dict[str, ClientSession]] = dict()

    def __init__(self, silence_exc: bool = False, **kwargs) -> None:
        """
        Constructor

        IN:
            silence_exc - whether or not silence client exceptions
            kwargs - additional kwargs to pass into the session object
                constructor
        """
        self.silence_exc = silence_exc

        sesh = ClientSession(**kwargs)
        self.session_map[id(self)] = sesh
        self.session = sesh

    async def get_summary(self):
        """
        Get a summary of the status page, including a status indicator, component statuses,
            unresolved incidents, and any upcoming or in-progress scheduled maintenances.

        OUT:
            dict or None
        """
        return await self.__fetch_json(SUMMARY_URL)

    async def get_status(self):
        """
        Get the status rollup for the whole page. This endpoint includes an indicator - one of
            none, minor, major, or critical, as well as a human description of
            the blended component status.

        OUT:
            dict or None
        """
        return await self.__fetch_json(STATUS_URL)

    async def get_components(self):
        """
        Get the components for the page. Each component is listed along with its status.

        OUT:
            dict or None
        """
        return await self.__fetch_json(COMPONENTS_URL)

    async def get_incidents(self):
        """
        Get a list of the 50 most recent incidents. This includes all unresolved incidents.

        OUT:
            dict or None
        """
        return await self.__fetch_json(INCIDENTS_URL)

    async def get_unresolved_incidents(self):
        """
        Get a list of any unresolved incidents.

        OUT:
            dict or None
        """
        return await self.__fetch_json(UNRESOLVED_INCIDENTS_URL)

    async def get_maintenances(self):
        """
        Get a list of the 50 most recent scheduled maintenances.

        OUT:
            dict or None
        """
        return await self.__fetch_json(MAINTENANCES_URL)

    async def get_upcoming_maintenances(self):
        """
        Get a list of any upcoming maintenances.

        OUT:
            dict or None
        """
        return await self.__fetch_json(UPCOMING_MAINTENANCES_URL)

    async def get_active_maintenances(self):
        """
        Get a list of any active maintenances.

        OUT:
            dict or None
        """
        return await self.__fetch_json(ACTIVE_MAINTENANCES_URL)

    async def close(self) -> None:
        """
        Method to close client connection.
        Must be ALWAYS called on program exit
        """
        await self.session.close()
        try:
            del self.session_map[id(self)]

        except KeyError:
            pass

    async def __aenter__(self) -> APIClient:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        traceback: Optional[TracebackType]
    ) -> None:
        await self.close()

    async def __fetch_json(self, page_url: str) -> JSONResponce:
        """
        Fetches json from an API endpoint

        IN:
            page_url - the page to fetch a json from

        OUT:
            dict or None
        """
        try:
            async with self.session.get(page_url) as resp:
                return await resp.json()

        except ClientError:
            if not self.silence_exc:
                raise

            return None

    @classmethod
    def check_sessions(cls) -> None:
        """
        Cleanup method
        """
        if cls.session_map:
            async def cleanup_coro():
                cleanup_fut = asyncio.gather(
                    *[sesh.close() for sesh in cls.session_map.values()],
                    return_exceptions=True
                )
                return await cleanup_fut

            asyncio.run(cleanup_coro())

atexit.register(APIClient.check_sessions)
