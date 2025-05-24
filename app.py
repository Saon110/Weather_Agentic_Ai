import streamlit as st
from weather_agent import get_weather
from firebase_chat import (
    create_new_chat,
    add_message,
    get_recent_messages,
    list_user_chats,
    delete_chat,
)
from voice_utils import record_and_transcribe, speak

st.set_page_config(page_title="Weather Assistant", page_icon="⛅")
st.title("💬 Weather Assistant")
st.caption("Ask your weather-related questions and get accurate answers.")

# Initialize session state
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "voice_input" not in st.session_state:
    st.session_state.voice_input = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# --- Sidebar Chat Management ---
st.sidebar.title("🗂 Chats")

try:
    for chat_id, created in list_user_chats():
        label = f"{created.strftime('%Y-%m-%d %H:%M:%S')}" if created else chat_id
        col1, col2 = st.sidebar.columns([0.8, 0.2])
        with col1:
            if st.button(label, key=f"select_{chat_id}"):
                st.session_state.chat_id = chat_id
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}"):
                delete_chat(chat_id)
                if st.session_state.chat_id == chat_id:
                    st.session_state.chat_id = None
                st.rerun()
except Exception as e:
    st.sidebar.error("Error loading chats.")
    st.sidebar.exception(e)

if st.sidebar.button("➕ New Chat"):
    try:
        st.session_state.chat_id = create_new_chat()
    except Exception as e:
        st.sidebar.error("Error creating new chat.")
        st.sidebar.exception(e)

# --- Load and Display Messages ---
if st.session_state.chat_id:
    try:
        messages = list(get_recent_messages(st.session_state.chat_id))
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    except Exception as e:
        st.error("Error loading messages.")
        st.exception(e)

# --- Input Section ---
input_col, voice_col = st.columns([4, 1])
with input_col:
    user_input = st.chat_input("Enter your weather query or press mic...")
with voice_col:
    if st.button("🎤", use_container_width=True, help="Record voice input"):
        st.session_state.processing = True

# --- Voice Input Handling ---
if st.session_state.processing:
    with st.spinner("Recording (10s max)..."):
        transcribed_text = record_and_transcribe()
        st.session_state.processing = False
        
        if transcribed_text.startswith("❌"):
            st.error(transcribed_text)
        else:
            st.session_state.voice_input = transcribed_text
    st.rerun()

# --- Process Inputs ---
final_input = user_input or st.session_state.pop("voice_input", None)

if final_input:
    # Auto-create chat if none exists
    if not st.session_state.chat_id:
        try:
            st.session_state.chat_id = create_new_chat()
            # st.sidebar.success("Created new chat automatically!")
        except Exception as e:
            st.error("Failed to create new chat")
            st.exception(e)
            final_input = None

    if final_input and st.session_state.chat_id:
        # Display user message
        with st.chat_message("user"):
            st.markdown(final_input)

        try:
            # Add to Firebase
            add_message(st.session_state.chat_id, "user", final_input)

            # Get response
            with st.spinner("🔍 Analyzing weather..."):
                response = get_weather(final_input)

            # Add assistant response
            add_message(st.session_state.chat_id, "assistant", response)

            # Display response
            with st.chat_message("assistant"):
                st.markdown(response)
                try:
                    speak(response)
                except Exception as e:
                    st.warning(f"🔇 Voice output failed: {e}")

        except Exception as e:
            st.error("⚠️ Something went wrong processing your request.")
            st.exception(e)