import streamlit as st
import time
from agent import process_customer_query
from database import DB_PATH
import sqlite3

st.set_page_config(
    page_title="Apex TechGear Support",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .st-emotion-cache-1c7y2kd {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with DB records and Policies for easy demo inspection
with st.sidebar:
    st.title("📦 Store Control Center")
    st.caption("Inspect live database & test queries")
    
    st.subheader("Live Customer Orders")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, status, total FROM orders")
    rows = cursor.fetchall()
    conn.close()
    
    for r in rows:
        st.markdown(f"**`{r[0]}`** — {r[1]}  \n*Status:* `{r[2]}` | *Total:* `${r[3]}`")
        st.divider()

    st.subheader("💡 Quick Test Prompts")
    quick_prompts = [
        "Where is my package for order #1026?",
        "Can I return my order #1025?",
        "Why is there a charge for cancelled order #1024?",
        "What is your return policy?"
    ]
    for qp in quick_prompts:
        if st.button(qp, use_container_width=True):
            st.session_state["user_input_preset"] = qp

# Main Chat Header
st.title("🎧 Apex TechGear AI Support")
st.markdown("Ask anything about your orders, tracking, refunds, or store policies.")

# Session state message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm Alex from Apex TechGear support. How can I help you today?"}
    ]

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle preset prompt or user input
user_query = st.chat_input("Type your message or order question here...")
if "user_input_preset" in st.session_state and st.session_state["user_input_preset"]:
    user_query = st.session_state["user_input_preset"]
    st.session_state["user_input_preset"] = None

if user_query:
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Alex is checking policies and orders..."):
            result = process_customer_query(user_query)
            bot_reply = result.get("answer", "I'm sorry, I couldn't process your request.")
            st.markdown(bot_reply)
            
            # If an order was found, show a small nice info badge
            if result.get("order_data"):
                od = result["order_data"]
                st.caption(f"🔍 Grounded with verified record for: **{od['id']}** ({od['customer_name']})")
                
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})