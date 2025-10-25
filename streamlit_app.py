import streamlit as st
from openai import OpenAI

# --- App 기본 설정 ---
st.set_page_config(page_title="Chatbot", page_icon="💬")
st.title("💬나의 챗봇~~~")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "You can manage your OpenAI API key safely via `.streamlit/secrets.toml`."
)

# --- API 키 로드 ---
try:
    openai_api_key = st.secrets["general"]["OPENAI_API_KEY"]
except Exception:
    st.error("❌ OpenAI API key not found in `.streamlit/secrets.toml`.")
    st.stop()

# --- OpenAI 클라이언트 생성 ---
client = OpenAI(api_key=openai_api_key)

# --- 세션 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 테스트 버튼 (대화 초기화) ---
if st.button("대화 초기화"):
    st.session_state.messages = []
    st.rerun()

# --- 기존 메시지 출력 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 입력창 ---
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 모델 응답 스트리밍 ---
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            for chunk in client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                content = getattr(chunk.choices[0].delta, "content", "")
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"⚠️ API 요청 중 오류 발생: {e}")
            st.stop()

    # --- 응답 저장 ---
    st.session_state.messages.append({"role": "assistant", "content": full_response})
