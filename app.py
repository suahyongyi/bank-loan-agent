import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Bank Loan Agent",
    page_icon="🏦",
    layout="centered"
)

# --- 🔒 AUTHENTICATION GATE ---
# 1. Define the password
ACCESS_PASSWORD = "iti122" 

# 2. Check Authentication Status
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 3. Login Screen
if not st.session_state.authenticated:
    st.title("🔒 Restricted Access")
    st.markdown("### Bank Loan Prototype")
    st.write("Please enter the access password to view the prototype.")
    
    password_input = st.text_input("Enter Access Password", type="password")
    
    if st.button("Login"):
        if password_input == ACCESS_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()  # Reload the app to show the main interface
        else:
            st.error("❌ Incorrect password.")
    
    st.stop() # 🛑 This STOPS the app here. No API calls will be made.

# ==========================================
#      MAIN APP
# ==========================================

st.title("🏦 Bank Loan Processing Agent")

# --- SESSION MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: RESET BUTTON ---
with st.sidebar:
    st.header("Controls")
    if st.button("🗑️ Reset Conversation", type="primary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Session ID:\n{st.session_state.session_id}")

# --- SECURELY LOAD API URL ---
try:
    API_URL = st.secrets["FLOWISE_API_URL"]
except FileNotFoundError:
    st.error("⚠️ API URL missing! Please check your configuration.")
    st.stop()
except KeyError:
    st.error("⚠️ 'FLOWISE_API_URL' key not found in secrets.")
    st.stop()

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- HANDLE USER INPUT ---
if prompt := st.chat_input("Enter Customer ID or ask a question..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Connecting to Agent..."):
            try:
                payload = {
                    "question": prompt,
                    "overrideConfig": {
                        "sessionId": st.session_state.session_id
                    }
                }
                
                response = requests.post(API_URL, json=payload)
                response.raise_for_status()
                output = response.json()
                
                if isinstance(output, dict) and "text" in output:
                    bot_text = output["text"]
                elif isinstance(output, dict) and "json" in output:
                    bot_text = str(output["json"])
                else:
                    bot_text = str(output)

                st.markdown(bot_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_text})

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection Error: {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")