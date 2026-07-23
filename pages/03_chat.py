import streamlit as st

from src.auth.service import getCurrentUserId, requireLogin
from src.chat.guard import getMedicalRefusal
from src.chat.repository import ChatRepository
from src.chat.service import streamResearchAnswer
from src.ui.theme import applyTheme


requireLogin()
applyTheme()
st.title("연구 챗봇")
st.caption("PubMed 메타데이터와 연구 맥락을 묻는 공간입니다. 개인 의료 조언은 제공하지 않습니다.")

ownerId = getCurrentUserId()
repository: ChatRepository | None = None
repositoryError = False

try:
    repository = ChatRepository()
except Exception:
    repositoryError = True

if "chatMessages" not in st.session_state:
    if repository is not None:
        try:
            st.session_state.chatMessages = repository.loadMessages(ownerId)
        except Exception:
            st.session_state.chatMessages = []
            repositoryError = True
    else:
        st.session_state.chatMessages = []

if repositoryError:
    st.warning("대화 저장소에 연결하지 못해 현재 브라우저 세션에서만 대화를 유지합니다.")

if not st.session_state.chatMessages:
    st.info("논문 동향, 초록 해석, 연구 주제 비교를 질문해 보세요.")

for message in st.session_state.chatMessages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("연구 질문을 입력하세요")
if question:
    userMessage = {"role": "user", "content": question}
    st.session_state.chatMessages.append(userMessage)
    with st.chat_message("user"):
        st.markdown(question)
    if repository is not None:
        try:
            repository.saveMessage(ownerId, "user", question)
        except Exception:
            st.warning("이번 질문은 서버에 저장되지 않았습니다.")

    refusal = getMedicalRefusal(question)
    with st.chat_message("assistant"):
        if refusal:
            answer = refusal
            st.markdown(answer)
        else:
            try:
                answer = st.write_stream(streamResearchAnswer(st.session_state.chatMessages))
            except Exception:
                answer = "응답을 생성하지 못했습니다. OpenAI 설정과 API 사용 한도를 확인해 주세요."
                st.error(answer)
    assistantMessage = {"role": "assistant", "content": answer}
    st.session_state.chatMessages.append(assistantMessage)
    if repository is not None:
        try:
            repository.saveMessage(ownerId, "assistant", answer)
        except Exception:
            st.warning("이번 답변은 서버에 저장되지 않았습니다.")
