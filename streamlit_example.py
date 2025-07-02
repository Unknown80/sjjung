import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Page config
st.set_page_config(page_title="Multi-Chat Assistant", page_icon="💬", layout="wide")

# Initialize session state for multiple chats and API key
if 'chats' not in st.session_state:
    st.session_state.chats = {
        "General": [{"role": "ai", "content": "Hello! How can I assist you with general questions?"}],
        "Technical Support": [{"role": "ai", "content": "Hello! How can I help you with technical issues?"}],
        "Ideas": [{"role": "ai", "content": "Hello! What ideas would you like to discuss?"}]
    }
    st.session_state.active_chat = "General"
    st.session_state.api_key = ""

# Sidebar for chat management and settings
with st.sidebar:
    st.title("🔑 API Key")
    
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
    
    st.divider()
    
    st.title("💬 Chat Rooms")
    
    # Create new chat
    new_chat_name = st.text_input("Create new chat room:")
    if st.button("+") and new_chat_name:
        if new_chat_name not in st.session_state.chats:
            st.session_state.chats[new_chat_name] = [{"role": "ai", "content": f"Hello! Welcome to {new_chat_name}. How can I help you?"}]
            st.session_state.active_chat = new_chat_name
            st.rerun()
        else:
            st.error(f"Chat room '{new_chat_name}' already exists.")
    
    # List of chats
    st.write("### Your Chats")
    for chat_name in list(st.session_state.chats.keys()):
        if st.button(chat_name, key=f"btn_{chat_name}", use_container_width=True):
            st.session_state.active_chat = chat_name
            st.rerun()
    
    # Clear current chat
    if st.button("Clear Current Chat"):
        if st.session_state.active_chat in st.session_state.chats:
            st.session_state.chats[st.session_state.active_chat] = [{"role": "ai", "content": f"Chat cleared. How can I help you with {st.session_state.active_chat}?"}]
            st.rerun()

# Main chat interface
st.title(f"{st.session_state.active_chat if 'active_chat' in st.session_state else 'Chat'}")

# Check if API key is set
if not st.session_state.get("api_key"):
    st.warning("⚠️ Please enter your OpenAI API Key in the sidebar to start chatting.")
    st.stop()

# Display chat messages
for msg in st.session_state.chats.get(st.session_state.active_chat, []):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    user_msg = {"role": "user", "content": prompt}
    st.session_state.chats[st.session_state.active_chat].append(user_msg)
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate AI response
    with st.spinner("Thinking..."):
        try:
            chat = ChatOpenAI(
                model="gpt-4o", 
                temperature=0,
                openai_api_key=st.session_state.api_key
            )
            response = chat.invoke(prompt)
            ai_msg = {"role": "ai", "content": response.content}
            st.session_state.chats[st.session_state.active_chat].append(ai_msg)
            
            with st.chat_message("ai"):
                st.write(response.content)
                
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chats[st.session_state.active_chat].append({"role": "ai", "content": error_msg})
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