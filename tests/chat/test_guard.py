from src.chat.guard import MEDICAL_ADVICE_REFUSAL, getMedicalRefusal;


def testRefusesRequiredMedicalAdviceExample() -> None:
    assert getMedicalRefusal("음주 후 타이레놀 먹어도 되나요?") == MEDICAL_ADVICE_REFUSAL;


def testAllowsResearchMetadataQuestion() -> None:
    assert getMedicalRefusal("2024년 당뇨병 논문이 가장 많은 저널은?") is None;

