import streamlit as st
from openai import OpenAI
import base64

# Show title and description.
st.title("편리한 챗봇")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # 다중 대화 세션 초기화 (12번 기능)
    if "conversations" not in st.session_state:
        st.session_state.conversations = {"대화 1": []}
        st.session_state.current_conversation = "대화 1"
    
    if "messages" not in st.session_state:
        st.session_state.messages = st.session_state.conversations[st.session_state.current_conversation]
    
    # 토큰 사용량 초기화 (5번 기능)
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = {}
        for conv_name in st.session_state.conversations.keys():
            st.session_state.total_tokens[conv_name] = 0

    # 사이드바 구성
    with st.sidebar:
        st.subheader("💬 대화 목록")
        
        # 대화 선택 (12번 기능)
        selected = st.selectbox(
            "대화 선택",
            list(st.session_state.conversations.keys()),
            index=list(st.session_state.conversations.keys()).index(st.session_state.current_conversation)
        )
        
        if selected != st.session_state.current_conversation:
            # 현재 대화 저장
            st.session_state.conversations[st.session_state.current_conversation] = st.session_state.messages
            # 새 대화 로드
            st.session_state.current_conversation = selected
            st.session_state.messages = st.session_state.conversations[selected]
            st.rerun()
        
        # 새 대화 시작 (12번 기능)
        if st.button("➕ 새 대화"):
            # 현재 대화 저장
            st.session_state.conversations[st.session_state.current_conversation] = st.session_state.messages
            # 새 대화 생성
            new_name = f"대화 {len(st.session_state.conversations) + 1}"
            st.session_state.conversations[new_name] = []
            st.session_state.total_tokens[new_name] = 0
            st.session_state.current_conversation = new_name
            st.session_state.messages = []
            st.rerun()
        
        # 대화 초기화
        if st.button("현재 대화 초기화", type="secondary"):
            st.session_state.messages = []
            st.session_state.conversations[st.session_state.current_conversation] = []
            st.session_state.total_tokens[st.session_state.current_conversation] = 0
            st.rerun()
        
        st.divider()
        
        # 토큰 사용량 표시 (5번 기능)
        st.subheader("📊 토큰 사용량")
        current_tokens = st.session_state.total_tokens.get(st.session_state.current_conversation, 0)
        st.metric("현재 대화", f"{current_tokens:,} tokens")
        total_all = sum(st.session_state.total_tokens.values())
        st.metric("전체 대화", f"{total_all:,} tokens")
        
        st.divider()
        
        # 대화 검색 (9번 기능)
        st.subheader("🔍 대화 검색")
        search_query = st.text_input("검색어 입력")
        if search_query:
            matches = [
                (idx, msg) for idx, msg in enumerate(st.session_state.messages) 
                if search_query.lower() in msg["content"].lower() if isinstance(msg["content"], str)
            ]
            st.write(f"검색 결과: {len(matches)}개")
            for idx, msg in matches[:5]:  # 상위 5개만 표시
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                content_preview = msg["content"][:50] if isinstance(msg["content"], str) else "[이미지 포함]"
                with st.expander(f"{role_emoji} {content_preview}..."):
                    if isinstance(msg["content"], str):
                        st.write(msg["content"])
                    else:
                        st.write("이미지가 포함된 메시지입니다.")

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], str):
                st.markdown(message["content"])
            elif isinstance(message["content"], list):
                # 이미지가 포함된 메시지 처리
                for item in message["content"]:
                    if item["type"] == "text":
                        st.markdown(item["text"])
                    elif item["type"] == "image_url":
                        st.image(item["image_url"]["url"])

    # 이미지 업로드 (6번 기능)
    uploaded_image = st.file_uploader("🖼️ 이미지 업로드 (선택사항)", type=['png', 'jpg', 'jpeg'], key="image_uploader")

    # Create chat input field
    if prompt := st.chat_input("What is up?"):
        # 메시지 내용 준비
        if uploaded_image:
            # 이미지를 base64로 인코딩
            image_bytes = uploaded_image.read()
            image_base64 = base64.b64encode(image_bytes).decode()
            
            # 이미지가 포함된 메시지 구성
            message_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        else:
            message_content = prompt

        # Store and display user message
        st.session_state.messages.append({"role": "user", "content": message_content})
        with st.chat_message("user"):
            st.markdown(prompt)
            if uploaded_image:
                st.image(uploaded_image)

        # API 호출 메시지 준비
        api_messages = []
        for m in st.session_state.messages:
            if isinstance(m["content"], str):
