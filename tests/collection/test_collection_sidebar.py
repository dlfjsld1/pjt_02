"""Unit tests for collection sidebar submission behavior."""

from __future__ import annotations

from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

from src.collection.models import CollectionResult


class FakeSidebar:
    """A minimal Streamlit sidebar replacement for UI flow tests."""

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword
        self.errors: list[str] = []
        self.successes: list[str] = []

    def header(self, _label: str) -> None:
        return None

    def text_input(self, _label: str, *, key: str) -> str:
        return self.keyword

    def number_input(self, label: str, **_kwargs: object) -> int:
        values = {
            "검색 시작 연도": 2022,
            "검색 종료 연도": 2025,
            "최대 수집 논문 수": 100,
        }
        return values[label]

    def button(self, _label: str, *, key: str) -> bool:
        return True

    def error(self, message: str) -> None:
        self.errors.append(message)

    def success(self, message: str) -> None:
        self.successes.append(message)


class CollectionSidebarTest(unittest.TestCase):
    """Confirm only valid sidebar input invokes the collection workflow."""

    def test_render_collection_sidebar_collects_valid_input(self) -> None:
        sidebar = FakeSidebar("COVID-19 vaccine")
        streamlit = SimpleNamespace(sidebar = sidebar, session_state = {})
        expected_result = CollectionResult(2, 2, 2, 0, ["1001", "1002"])

        with patch.dict(sys.modules, {"streamlit": streamlit}):
            from components.collection_sidebar import render_collection_sidebar

            with patch(
                "components.collection_sidebar.collect_papers",
                return_value = expected_result,
            ) as collect_mock:
                result = render_collection_sidebar()

        collect_mock.assert_called_once_with("COVID-19 vaccine", 2022, 2025, 100)
        self.assertEqual(result.collection_result, expected_result)
        self.assertEqual(sidebar.successes, ["신규 2건, 중복 건너뜀 0건"])
        self.assertEqual(
            streamlit.session_state["collectionLastResult"],
            {"insertedCount": 2, "skippedCount": 0},
        )

    def test_render_collection_sidebar_does_not_collect_invalid_input(self) -> None:
        sidebar = FakeSidebar("   ")
        streamlit = SimpleNamespace(sidebar = sidebar, session_state = {})

        with patch.dict(sys.modules, {"streamlit": streamlit}):
            from components.collection_sidebar import render_collection_sidebar

            with patch("components.collection_sidebar.collect_papers") as collect_mock:
                result = render_collection_sidebar()

        collect_mock.assert_not_called()
        self.assertIsNone(result.collection_result)
        self.assertEqual(sidebar.errors, ["검색 키워드를 입력하세요."])
