"""Unit tests for protected-page authentication flow."""

from __future__ import annotations

from types import SimpleNamespace
import importlib
import sys
import unittest
from unittest.mock import Mock, patch


class AuthServiceTest(unittest.TestCase):
    """Ensure unauthenticated users cannot continue rendering protected pages."""

    def test_require_login_redirects_and_stops_execution(self) -> None:
        streamlit = SimpleNamespace(switch_page = Mock(), stop = Mock())

        with patch.dict(sys.modules, {"streamlit": streamlit}):
            sys.modules.pop("src.auth.service", None)
            service = importlib.import_module("src.auth.service")
            with (
                patch.object(service, "is_auth_configured", return_value = True),
                patch.object(service, "is_logged_in", return_value = False),
            ):
                service.require_login()

        streamlit.switch_page.assert_called_once_with("app.py")
        streamlit.stop.assert_called_once_with()
