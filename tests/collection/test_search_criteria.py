"""Unit tests for collection search input validation."""

import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.collection.search_criteria import (
    MAX_RESULTS,
    PUBMED_ESEARCH_URL,
    build_search_request,
    get_ncbi_api_key,
    validate_search_criteria,
)


class SearchCriteriaTest(unittest.TestCase):
    """Validate collection search inputs without calling the PubMed API."""

    def test_validate_search_criteria_trims_keyword(self) -> None:
        criteria, errors = validate_search_criteria(" COVID-19 vaccine ", 2022, 2025, 100)

        self.assertEqual(errors, [])
        self.assertIsNotNone(criteria)
        self.assertEqual(criteria.keyword, "COVID-19 vaccine")
        self.assertEqual(criteria.max_results, MAX_RESULTS)

    def test_validate_search_criteria_rejects_blank_keyword(self) -> None:
        criteria, errors = validate_search_criteria("   ", 2022, 2025, 100)

        self.assertIsNone(criteria)
        self.assertIn("검색 키워드를 입력하세요.", errors)

    def test_validate_search_criteria_rejects_reversed_years(self) -> None:
        criteria, errors = validate_search_criteria("COVID-19 vaccine", 2025, 2022, 100)

        self.assertIsNone(criteria)
        self.assertIn("검색 시작 연도는 종료 연도보다 클 수 없습니다.", errors)

    def test_validate_search_criteria_rejects_out_of_range_max_results(self) -> None:
        low_criteria, low_errors = validate_search_criteria("COVID-19 vaccine", 2022, 2025, 0)
        high_criteria, high_errors = validate_search_criteria("COVID-19 vaccine", 2022, 2025, 101)

        self.assertIsNone(low_criteria)
        self.assertIsNone(high_criteria)
        self.assertIn("최대 수집 논문 수는 1~100 사이여야 합니다.", low_errors)
        self.assertIn("최대 수집 논문 수는 1~100 사이여야 합니다.", high_errors)

    def test_build_search_request_uses_environment_api_key(self) -> None:
        criteria, errors = validate_search_criteria("COVID-19 vaccine", 2022, 2025, 100)
        url, parameters = build_search_request(criteria, {"NCBI_API_KEY": "test-key"})

        self.assertEqual(errors, [])
        self.assertEqual(url, PUBMED_ESEARCH_URL)
        self.assertEqual(parameters["api_key"], "test-key")
        self.assertEqual(parameters["retmax"], 100)

    def test_get_ncbi_api_key_returns_none_for_blank_value(self) -> None:
        self.assertIsNone(get_ncbi_api_key({"NCBI_API_KEY": "  "}))

    def test_get_ncbi_api_key_reads_streamlit_secret_when_environment_is_not_injected(self) -> None:
        config_module = SimpleNamespace(get_ncbi_api_key=lambda: "test-api-key")
        with patch.dict(sys.modules, {"src.config": config_module}):
            self.assertEqual(get_ncbi_api_key(), "test-api-key")

    def test_build_search_request_uses_streamlit_secret_without_exposing_it_in_errors(self) -> None:
        criteria, errors = validate_search_criteria("COVID-19 vaccine", 2022, 2025, 3)

        config_module = SimpleNamespace(get_ncbi_api_key=lambda: "test-api-key")
        with patch.dict(sys.modules, {"src.config": config_module}):
            _, parameters = build_search_request(criteria)

        self.assertEqual(errors, [])
        self.assertEqual(parameters["api_key"], "test-api-key")
        self.assertNotIn("test-api-key", " ".join(errors))
