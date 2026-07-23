from src.chat.guard import MEDICAL_ADVICE_REFUSAL, get_medical_refusal


def test_refuses_required_medical_advice_example() -> None:
    assert get_medical_refusal("음주 후 타이레놀 먹어도 되나요?") == MEDICAL_ADVICE_REFUSAL


def test_allows_research_metadata_question() -> None:
    assert get_medical_refusal("2024년 당뇨병 논문이 가장 많은 저널은?") is None

