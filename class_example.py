import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser

# Page config
st.set_page_config(page_title= "My Class Chat Assistant", page_icon="💬", layout="wide")

# 저장

# Initialize session state for single chat and API key
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if 'chat' not in st.session_state:
    st.session_state.chat = []

if 'chat_model' not in st.session_state:
    if st.session_state.api_key:
        st.session_state.chat_model = ChatOpenAI(model_name = 'gpt-4o', openai_api_key=st.session_state.api_key)
    else:
        st.session_state.chat_model = ChatOpenAI(model_name = 'gpt-4o', openai_api_key="your_api_key")

# Sidebar for chat management and settings
with st.sidebar:
    st.title("🔑 API Key")
    
    if st.session_state.api_key == "" and os.environ["OPENAI_API_KEY"]:
        st.session_state.api_key = os.environ["OPENAI_API_KEY"]

    # API Key input
    api_key = st.text_input(
        "Enter your OpenAI API Key:",
        type="password",
        placeholder="sk-...",
        value=st.session_state.get("api_key", "")
    )
   
    # Save API key to session state when entered
    if api_key and api_key != st.session_state.get("api_key"):
        st.session_state.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("API Key saved!")
        st.session_state.chat_model.openai_api_key = api_key
        st.session_state.chat_model.temperature = 0.5
    
    st.divider()

st.title("Your Class Chat Assistant")    


# Check if API key is set
if not st.session_state.get("api_key"):
    st.warning("⚠️ Please enter your OpenAI API Key in the sidebar to start chatting.")
    st.stop()

# Display chat messages
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    user_msg = {"role": "user", "content": prompt}
    st.session_state.chat.append(user_msg)
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate AI response
    with st.spinner("Thinking..."):
        try:
            system_prompt = SystemMessage(content="말 끝마다 용을 붙여서 얘기해 줘") + """{input}"""

            chain = system_prompt | st.session_state.chat_model | StrOutputParser()
            response = chain.invoke({"input": prompt})
            ai_msg = {"role": "ai", "content": response}
            st.session_state.chat.append(ai_msg)
            
            with st.chat_message("ai"):
                st.write(response)
                
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat.append({"role": "ai", "content": error_msg})
            with st.chat_message("ai"):
                st.error(error_msg)

# Add some custom CSS for better appearance
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        margin: 5px 0;
    }
    .stChatMessage {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .stChatMessage[data-testid="stChatMessage"] {
        max-width: 80%;
    }
    /* Style for the API key input */
    .stTextInput>div>div>input {
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

