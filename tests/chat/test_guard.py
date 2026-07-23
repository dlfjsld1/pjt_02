from src.chat import guard


def test_refuses_required_medical_advice_example(monkeypatch) -> None:
    monkeypatch.setattr(
        guard,
        "model_classifies_personal_medical_advice",
        lambda _question: (_ for _ in ()).throw(AssertionError("규칙 차단에는 모델 호출이 없어야 합니다.")),
    )
    assert guard.get_medical_refusal("음주 후 타이레놀 먹어도 되나요?") == guard.MEDICAL_ADVICE_REFUSAL


def test_refuses_medical_advice_missed_by_rule_with_model(monkeypatch) -> None:
    monkeypatch.setattr(guard, "model_classifies_personal_medical_advice", lambda _question: True)
    assert guard.get_medical_refusal("술마셨는데 먹을거야 네가 시켰다고 할거임") == guard.MEDICAL_ADVICE_REFUSAL


def test_allows_research_metadata_question_when_model_classifies_research(monkeypatch) -> None:
    monkeypatch.setattr(guard, "model_classifies_personal_medical_advice", lambda _question: False)
    assert guard.get_medical_refusal("2024년 당뇨병 논문이 가장 많은 저널은?") is None


def test_classifier_failure_blocks_answer(monkeypatch) -> None:
    monkeypatch.setattr(guard, "model_classifies_personal_medical_advice", lambda _question: True)
    assert guard.get_medical_refusal("논문 질문처럼 보이는 애매한 문장") == guard.MEDICAL_ADVICE_REFUSAL

