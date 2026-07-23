"""Unit tests for collection search input validation."""

import unittest

from src.collection.searchCriteria import (
    MAX_RESULTS,
    PUBMED_ESEARCH_URL,
    buildSearchRequest,
    getNcbiApiKey,
    validateSearchCriteria,
)


class SearchCriteriaTest(unittest.TestCase):
    """Validate collection search inputs without calling the PubMed API."""

    def testValidateSearchCriteriaTrimsKeyword(self) -> None:
        criteria, errors = validateSearchCriteria(" COVID-19 vaccine ", 2022, 2025, 100)

        self.assertEqual(errors, [])
        self.assertIsNotNone(criteria)
        self.assertEqual(criteria.keyword, "COVID-19 vaccine")
        self.assertEqual(criteria.maxResults, MAX_RESULTS)

    def testValidateSearchCriteriaRejectsBlankKeyword(self) -> None:
        criteria, errors = validateSearchCriteria("   ", 2022, 2025, 100)

        self.assertIsNone(criteria)
        self.assertIn("검색 키워드를 입력하세요.", errors)

    def testValidateSearchCriteriaRejectsReversedYears(self) -> None:
        criteria, errors = validateSearchCriteria("COVID-19 vaccine", 2025, 2022, 100)

        self.assertIsNone(criteria)
        self.assertIn("검색 시작 연도는 종료 연도보다 클 수 없습니다.", errors)

    def testValidateSearchCriteriaRejectsOutOfRangeMaxResults(self) -> None:
        lowCriteria, lowErrors = validateSearchCriteria("COVID-19 vaccine", 2022, 2025, 0)
        highCriteria, highErrors = validateSearchCriteria("COVID-19 vaccine", 2022, 2025, 101)

        self.assertIsNone(lowCriteria)
        self.assertIsNone(highCriteria)
        self.assertIn("최대 수집 논문 수는 1~100 사이여야 합니다.", lowErrors)
        self.assertIn("최대 수집 논문 수는 1~100 사이여야 합니다.", highErrors)

    def testBuildSearchRequestUsesEnvironmentApiKey(self) -> None:
        criteria, errors = validateSearchCriteria("COVID-19 vaccine", 2022, 2025, 100)
        url, parameters = buildSearchRequest(criteria, {"NCBI_API_KEY": "test-key"})

        self.assertEqual(errors, [])
        self.assertEqual(url, PUBMED_ESEARCH_URL)
        self.assertEqual(parameters["api_key"], "test-key")
        self.assertEqual(parameters["retmax"], 100)

    def testGetNcbiApiKeyReturnsNoneForBlankValue(self) -> None:
        self.assertIsNone(getNcbiApiKey({"NCBI_API_KEY": "  "}))
