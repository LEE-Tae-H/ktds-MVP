import streamlit as st
import datetime
from langchain_qa_new import convo_qa_chain, convert_streamlit_history_to_langchain


# 페이지 설정
st.set_page_config(page_title="장애조치 에이전트 ", page_icon="🤖", layout="wide")

# 제목
st.title("🤖 장애조치 에이전트")


if "messages" not in st.session_state:
    st.session_state.messages = []

# 초기 환영 메시지
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "안녕하세요! 장애조치 에이전트입니다.",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d")
    })


# 이전 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 왼쪽 사이드바에 대화 이력 메뉴 추가
with st.sidebar:
    st.header("💬 대화 이력")
    if "messages" in st.session_state and st.session_state.messages:
        from collections import defaultdict
        grouped = defaultdict(list)
        for msg in st.session_state.messages:
            date = msg.get("timestamp", "날짜없음")
            grouped[date].append(msg)
        for date in sorted(grouped.keys()):
            with st.expander(f"📅 {date}"):
                for msg in grouped[date]:
                    role = "👤" if msg["role"] == "user" else "🤖"
                    st.markdown(f"{role} {msg['content']}")
    else:
        st.info("아직 대화 이력이 없습니다.")

# 사용자 입력 받기
if prompt := st.chat_input("질문을 입력하세요."):
    today = datetime.date.today().isoformat()
    # 사용자 메시지 저장 (timestamp 추가)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": today
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    # LangChain 대화 이력 변환
    chat_history = convert_streamlit_history_to_langchain(st.session_state.messages[:-1])

    # 답변 생성
    with st.spinner("답변 생성 중..."):
        result = convo_qa_chain.invoke({
            "input": prompt,
            "chat_history": chat_history
        })
        answer = result["answer"] if "answer" in result else str(result)

    # 답변 저장 및 출력 (timestamp 추가)
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "timestamp": today
    })
    with st.chat_message("assistant"):
        st.markdown(answer)
        # 검색된 문서(context)도 함께 출력
        if "context" in result and result["context"]:
            st.markdown("---")
            with st.expander("🔎 참고한 자료 펼치기"):
                st.markdown("**🔎 참고 문서:**")
                if isinstance(result["context"], list):
                    for i, doc in enumerate(result["context"], 1):
                        st.markdown(f"**[{i}]** {doc.page_content}")
                else:
                    st.markdown(result["context"])

# 하단 정보
st.markdown("---")
st.caption("© 2025 장애조치 에이전트 // MVP")