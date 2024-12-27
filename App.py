import os
import json
import logging
import streamlit as st
import openai

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API Key from config.json
try:
    working_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(working_dir, "config.json")
    with open(config_path, "r") as f:
        config_data = json.load(f)
    OPENAI_API_KEY = config_data.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Missing OPENAI_API_KEY in configuration file.")
    openai.api_key = OPENAI_API_KEY
except FileNotFoundError:
    st.error("Configuration file not found. Please create a config.json file with the OpenAI API key.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error decoding config.json. Please ensure it contains valid JSON.")
    st.stop()
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# Configure Streamlit page
st.set_page_config(page_title="GPT-4o Chat", page_icon="💬", layout="centered")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [{"role": "system", "content": "You are a helpful assistant."}]

# Title
st.title("🤖 GPT-4o Chat")

# Display chat history
for message in st.session_state.chat_history[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_prompt = st.chat_input("Ask GPT-4o...")

if user_prompt and user_prompt.strip():
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Check and handle quota or API errors
    try:
        # API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.chat_history,
        )
        assistant_response = response["choices"][0]["message"]["content"]
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Display GPT-4o's response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
    except openai.error.RateLimitError:
        st.error("You have exceeded your current quota. Please check your OpenAI account usage.")
    except openai.error.AuthenticationError:
        st.error("Authentication error: Invalid API key. Please check your configuration.")
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API Error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
else:
    if user_prompt is not None:  # Only show warning if user interacted with input
        st.warning("Please enter a valid message.")

# Limit chat history to optimize performance
MAX_HISTORY = 10
if len(st.session_state.chat_history) > MAX_HISTORY:
    st.session_state.chat_history = st.session_state.chat_history[-MAX_HISTORY:]
