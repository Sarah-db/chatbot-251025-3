import streamlit as st
from openai import OpenAI

# 제목과 설명
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 🧹 대화 초기화 버튼 ("테스트")
    if st.button("테스트"):
        st.session_state.messages = []
        st.rerun()  # 최신 Streamlit에서 사용

    # 기존 대화 출력
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 모델 응답 스트리밍
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for chunk in client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # 응답 저장
        st.session_state.messages.append({"role": "assistant", "content": full_response})
