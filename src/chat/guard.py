import re


MEDICAL_ADVICE_REFUSAL = "이 앱은 PubMed 메타데이터 분석용이며, 개인 의료 조언, 진단, 처방 관련 질문에는 답변할 수 없습니다. 의료 관련 결정은 의료 전문가와 상담해 주세요."

PERSONAL_CONTEXT_PATTERN = re.compile(
    r"(나|저|제가|내가|나는|저는|먹어도|복용|증상|아픈|통증|괜찮을까|괜찮나요|어떻게 해야)",
    re.IGNORECASE,
)
MEDICAL_DECISION_PATTERN = re.compile(
    r"(약|타이레놀|진통제|항생제|처방|진단|복용|용량|몇 알|치료|수술|병원|의사|음주|술|임신)",
    re.IGNORECASE,
)
DIRECT_ADVICE_PATTERN = re.compile(
    r"(먹어도 (돼|되)|먹으면|복용해도|처방해|진단해|무슨 병|치료법|약 추천)",
    re.IGNORECASE,
)


def asks_for_personal_medical_advice(question: str) -> bool:
    normalized_question = " ".join(question.split())
    if DIRECT_ADVICE_PATTERN.search(normalized_question):
        return True
    return bool(
        PERSONAL_CONTEXT_PATTERN.search(normalized_question)
        and MEDICAL_DECISION_PATTERN.search(normalized_question)
    )


def get_medical_refusal(question: str) -> str | None:
    if asks_for_personal_medical_advice(question):
        return MEDICAL_ADVICE_REFUSAL
    return None

