from collections.abc import Iterator;
from typing import Any;

from openai import OpenAI;

from src.config import getOpenAiApiKey, getOpenAiModel;


SYSTEM_PROMPT = """당신은 PubMed 논문 메타데이터 탐색을 돕는 연구 보조 챗봇입니다.
논문 제목, 초록, 저널, 출판 연도 등 연구 정보에 관해 명확한 한국어로 답하세요.
개인 의료 조언, 진단, 처방은 하지 마세요. 근거가 없으면 모른다고 말하세요.""";


def buildModelInput(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    modelInput = [{"role": "system", "content": SYSTEM_PROMPT}];
    for message in messages[-20:]:
        role = str(message.get("role", ""));
        content = str(message.get("content", ""));
        if role in ("user", "assistant") and content:
            modelInput.append({"role": role, "content": content});
    return modelInput;


def streamResearchAnswer(messages: list[dict[str, Any]]) -> Iterator[str]:
    apiKey = getOpenAiApiKey();
    if not apiKey:
        raise RuntimeError("OpenAI API 키를 secrets.toml에 설정해 주세요.");
    client = OpenAI(api_key=apiKey);
    stream = client.responses.create(
        model=getOpenAiModel(),
        input=buildModelInput(messages),
        stream=True,
    );
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta;

