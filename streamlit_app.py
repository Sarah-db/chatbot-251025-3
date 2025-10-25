import streamlit as st
from openai import OpenAI
import base64

# Show title and description.
st.title("✦Simple Chatbot✦")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # 12. 다중 대화 세션 관리 초기화
    if "conversations" not in st.session_state:
        st.session_state.conversations = {"대화 1": []}
    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = "대화 1"
    
    # 현재 대화의 메시지 로드
    if "messages" not in st.session_state or st.session_state.messages != st.session_state.conversations[st.session_state.current_conversation]:
        st.session_state.messages = st.session_state.conversations[st.session_state.current_conversation]

    # 사이드바 구성
    with st.sidebar:
        st.subheader("💬 대화 목록")
        
        # 12. 대화 선택
        conversation_names = list(st.session_state.conversations.keys())
        selected = st.selectbox(
            "대화 선택",
            conversation_names,
            index=conversation_names.index(st.session_state.current_conversation)
        )
        
        if selected != st.session_state.current_conversation:
            # 현재 대화 저장
            st.session_state.conversations[st.session_state.current_conversation] = st.session_state.messages
            # 새 대화 로드
            st.session_state.current_conversation = selected
            st.session_state.messages = st.session_state.conversations[selected]
            st.rerun()
        
        # 12. 새 대화 시작
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ 새 대화", use_container_width=True):
                # 현재 대화 저장
                st.session_state.conversations[st.session_state.current_conversation] = st.session_state.messages
                # 새 대화 생성
                new_name = f"대화 {len(st.session_state.conversations) + 1}"
                st.session_state.conversations[new_name] = []
                st.session_state.current_conversation = new_name
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.conversations[st.session_state.current_conversation] = []
                st.session_state.messages = []
                st.rerun()
        
        st.divider()
        
        # 9. 대화 검색 기능
        st.subheader("🔍 대화 검색")
        search_query = st.text_input("검색어 입력", key="search_input")
        if search_query:
            matches = [
                (idx, msg) for idx, msg in enumerate(st.session_state.messages) 
                if search_query.lower() in msg["content"].lower() if isinstance(msg["content"], str)
            ]
            st.write(f"검색 결과: {len(matches)}개")
            for idx, msg in matches[:5]:  # 상위 5개만 표시
                role_text = "사용자" if msg["role"] == "user" else "챗봇"
                preview = msg["content"][:50] if isinstance(msg["content"], str) else "[이미지 포함 메시지]"
                with st.expander(f"{role_text}: {preview}..."):
                    if isinstance(msg["content"], str):
                        st.write(msg["content"])
                    else:
                        st.write("이미지가 포함된 메시지입니다.")
        
        st.divider()
        
        # 6. 이미지 업로드 (GPT-4 Vision용)
        st.subheader("🖼️ 이미지 업로드")
        st.caption("GPT-4 Vision 모델에서 사용 가능")

    # Display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], str):
                st.markdown(message["content"])
            elif isinstance(message["content"], list):
                # 이미지와 텍스트가 포함된 메시지 처리
                for item in message["content"]:
                    if item["type"] == "text":
                        st.markdown(item["text"])
                    elif item["type"] == "image_url":
                        st.caption("📷 이미지가 전송되었습니다")

    # 6. 이미지 업로드 처리
    uploaded_image = st.file_uploader("이미지 선택 (선택사항)", type=['png', 'jpg', 'jpeg'], key="image_uploader")
    
    # Create a chat input field
    if prompt := st.chat_input("What is up?"):
        # 메시지 내용 준비
        if uploaded_image:
            # 이미지를 base64로 인코딩
            image_bytes = uploaded_image.read()
            image_base64 = base64.b64encode(image_bytes).decode()
            
            # 이미지와 텍스트를 포함한 메시지 구성
            message_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
            
            # 사용자 메시지 저장 및 표시
            st.session_state.messages.append({"role": "user", "content": message_content})
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption("📷 이미지가 전송되었습니다")
        else:
            # 텍스트만 있는 메시지
            message_content = prompt
            st.session_state.messages.append({"role": "user", "content": message_content})
            with st.chat_message("user"):
                st.markdown(prompt)

        # API 호출을 위한 메시지 준비
        api_messages = []
        for msg in st.session_state.messages:
            if isinstance(msg["content"], str):
                api_messages.append({"role": msg["role"], "content": msg["content"]})
            else:
                # 리스트 형태의 content (이미지 포함)
                api_messages.append({"role": msg["role"], "content": msg["content"]})

        # Generate a response using the OpenAI API
        try:
            # 이미지가 있으면 gpt-4-vision-preview 사용, 없으면 gpt-3.5-turbo 사용
            model_to_use = "gpt-4o" if uploaded_image else "gpt-3.5-turbo"
            
            stream = client.chat.completions.create(
                model=model_to_use,
                messages=api_messages,
                stream=True,
            )

            # Stream the response to the chat
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 현재 대화를 conversations에 저장
            st.session_state.conversations[st.session_state.current_conversation] = st.session_state.messages
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            # 오류 발생 시 마지막 메시지 제거
            if st.session_state.messages:
                st.session_state.messages.pop()
