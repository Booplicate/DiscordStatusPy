
import unittest
from unittest.mock import patch
import inspect
from collections import defaultdict
from typing import Any


import DiscordStatusPy
from DiscordStatusPy import APIClient
from DiscordStatusPy.client import ClientError


JSONResponce = lambda: defaultdict(JSONResponce)

class _Mixin():
    TOTAL_API_ACCESSORS = 8

class TestClient(unittest.IsolatedAsyncioTestCase, _Mixin):
    """
    Test case for APIClient
    """
    async def asyncSetUp(self) -> None:
        self.client = APIClient()

    async def asyncTearDown(self) -> None:
        try:
            await self.client.close()
            del self.client

        except AttributeError:
            pass

    async def test_content_manager(self) -> None:
        self.assertFalse(self.client.closed)
        await self.client.close()
        self.assertTrue(self.client.closed)

        async with APIClient() as api_client:
            self.assertFalse(api_client.closed)

        self.assertTrue(api_client.closed)

    def test_apiclient_auto_cleanup(self) -> None:
        self.assertFalse(self.client.closed)
        APIClient.check_sessions()
        self.assertTrue(self.client.closed)

    @patch("DiscordStatusPy.APIClient._APIClient__fetch_json", return_value=JSONResponce())
    async def test_api_accessors(self, mock_fetch_json) -> None:
        def predicate(argument: Any) -> bool:
            return (
                inspect.ismethod(argument)
                and inspect.iscoroutinefunction(argument)
                and argument.__name__.startswith("get_")
            )

        members = inspect.getmembers(self.client, predicate)

        self.assertEqual(len(members), self.TOTAL_API_ACCESSORS)

        msg = "Case: API accessors should return dicts"
        for name, method in members:
            with self.subTest(msg):
                rv = await method()
                self.assertIsInstance(rv, defaultdict)

    async def test_exc_raising(self) -> None:
        with patch.object(self.client.session, "get", side_effect=ClientError) as mock:
            self.client.silence_exc = True

            try:
                await self.client.get_summary()
            except ClientError:
                self.fail("ClientError wasn't silenced.")

            self.client.silence_exc = False

            with self.assertRaises(ClientError, msg="ClientError wasn't raised."):
                await self.client.get_summary()

        class TestException(Exception): pass

        with patch.object(self.client.session, "get", side_effect=TestException) as mock:
            self.client.silence_exc = True

            with self.assertRaises(TestException, msg="TestException wasn't raised."):
                await self.client.get_summary()

class TestAPIFuncs(unittest.IsolatedAsyncioTestCase, _Mixin):
    """
    Test case for API functions
    """
    @patch("DiscordStatusPy.APIClient._APIClient__fetch_json", return_value=JSONResponce())
    async def test_api_functions(self, mock_fetch_json) -> None:
        def predicate(argument: Any) -> bool:
            return (
                inspect.iscoroutinefunction(argument)
                and argument.__name__.startswith("get_")
            )

        members = inspect.getmembers(DiscordStatusPy, predicate)

        self.assertEqual(len(members), self.TOTAL_API_ACCESSORS)

        msg = "Case: API access functions should return dicts"
        for name, function in members:
            with self.subTest(msg):
                rv = await function()
                self.assertIsInstance(rv, defaultdict)
