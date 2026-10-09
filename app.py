import streamlit as st
import uuid
from datetime import datetime, timedelta
from src.retrieve import retrieve
from src.generate import generate_answer

# ---------- Page Config ----------
st.set_page_config(
    page_title="IR Prohori",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- DeepSeek-inspired CSS ----------
st.markdown("""
<style>
    /* Hide Streamlit default header/menu */
    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Main app background */
    .stApp {
        background-color: #212121;
        color: #ececec;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2a2a2a;
        padding-top: 12px;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0 12px;
    }

    /* Sidebar logo */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 8px 18px 8px;
        border-bottom: 1px solid #2a2a2a;
        margin-bottom: 12px;
    }
    .sidebar-logo .logo-icon {
        font-size: 24px;
    }
    .sidebar-logo .logo-text {
        font-size: 18px;
        font-weight: 600;
        color: #ececec;
    }

    /* New Chat Button (top) */
    div[data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        color: #ececec;
        border: 1px solid #3a3a3a;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        text-align: left;
        width: 100%;
        transition: all 0.15s ease;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2a2a2a;
        border-color: #4a4a4a;
    }

    /* Chat history list */
    .chat-item button {
        background-color: transparent !important;
        color: #b0b0b0 !important;
        border: none !important;
        text-align: left !important;
        font-size: 13.5px !important;
        padding: 8px 10px !important;
        border-radius: 8px !important;
        width: 100% !important;
        font-weight: 400 !important;
        transition: background 0.15s ease !important;
    }
    .chat-item button:hover {
        background-color: #2a2a2a !important;
        color: #ececec !important;
    }

    /* Section header */
    .section-header {
        color: #6a6a6a;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin: 16px 0 6px 4px;
    }

    /* User message bubble */
    .user-msg {
        background-color: #2f2f2f;
        color: #ececec;
        padding: 12px 18px;
        border-radius: 18px;
        margin: 10px 0 10px auto;
        max-width: 70%;
        width: fit-content;
        font-size: 15px;
        line-height: 1.5;
    }

    /* Bot message bubble */
    .bot-msg {
        background-color: transparent;
        color: #ececec;
        padding: 12px 18px;
        border-radius: 18px;
        margin: 10px auto 10px 0;
        max-width: 75%;
        width: fit-content;
        font-size: 15px;
        line-height: 1.7;
        border: 1px solid #2a2a2a;
    }

    /* Welcome area */
    .welcome {
        text-align: center;
        color: #8a8a8a;
        margin-top: 80px;
        font-size: 22px;
        font-weight: 500;
    }
    .welcome-sub {
        text-align: center;
        color: #6a6a6a;
        font-size: 14px;
        margin-top: 8px;
    }

    /* Chat input */
    div[data-testid="stChatInput"] {
        background-color: #2f2f2f !important;
        border-radius: 24px !important;
        border: 1px solid #3a3a3a !important;
        padding: 4px 8px !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #ececec !important;
        font-size: 15px !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #7a7a7a !important;
    }

    /* Selectbox */
    div[data-testid="stSelectbox"] > div > div {
        background-color: #2a2a2a;
        color: #ececec;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {
        "title": "New Chat",
        "messages": [],
        "created": datetime.now()
    }
    st.session_state.current_chat_id = new_id

# ---------- Helpers ----------
def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {
        "title": "New Chat",
        "messages": [],
        "created": datetime.now()
    }
    st.session_state.current_chat_id = new_id

def get_current_chat():
    return st.session_state.chats[st.session_state.current_chat_id]

# ---------- Sidebar ----------
with st.sidebar:
    # Logo
    st.markdown("""
        <div class="sidebar-logo">
            <span class="logo-icon">🛡️</span>
            <span class="logo-text">IR Prohori</span>
        </div>
    """, unsafe_allow_html=True)

    # New Chat button
    if st.button("✏️  New Chat", key="new_chat_top"):
        create_new_chat()
        st.rerun()

    # Role selector
    role = st.selectbox("Role", ["Student", "Ambassador", "Admin"], label_visibility="collapsed")

    # Chat History by date
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    groups = {"Today": [], "Yesterday": [], "Earlier": []}

    for chat_id, chat_data in reversed(list(st.session_state.chats.items())):
        created = chat_data.get("created", datetime.now()).date()
        if created == today:
            groups["Today"].append((chat_id, chat_data))
        elif created == yesterday:
            groups["Yesterday"].append((chat_id, chat_data))
        else:
            groups["Earlier"].append((chat_id, chat_data))

    for group_name, items in groups.items():
        if items:
            st.markdown(f"<div class='section-header'>{group_name}</div>", unsafe_allow_html=True)
            for chat_id, chat_data in items:
                title = chat_data["title"]
                st.markdown('<div class="chat-item">', unsafe_allow_html=True)
                if st.button(title, key=f"chat_{chat_id}"):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Bottom: user info
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='border-top: 1px solid #2a2a2a; padding-top: 12px; "
        "color: #8a8a8a; font-size: 12px;'>"
        "👤 Md Iftiur Hossen Riyad<br>"
        "<span style='color: #5a5a5a;'>#DigitalProhori</span></div>",
        unsafe_allow_html=True
    )

# ---------- Main Area ----------
current_chat = get_current_chat()

# Header (only if no messages)
if not current_chat["messages"]:
    st.markdown("""
        <div class="welcome">🛡️ IR Prohori</div>
        <div class="welcome-sub">
            A security-first AI assistant for digital safety
        </div>
        <div class="welcome-sub" style="margin-top: 20px; color: #5a5a5a;">
            Try: "How to report online harassment?"
        </div>
    """, unsafe_allow_html=True)
else:
    # Small header for active chat
    st.markdown(
        f"<div style='color: #8a8a8a; font-size: 13px; padding: 4px 0 12px 0;'>"
        f"{current_chat['title']}</div>",
        unsafe_allow_html=True
    )

# Display messages
for msg in current_chat["messages"]:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# ---------- Input Box ----------
query = st.chat_input("Message IR Prohori...")

if query:
    current_chat["messages"].append({"role": "user", "content": query})

    if current_chat["title"] == "New Chat":
        current_chat["title"] = query[:28] + ("..." if len(query) > 28 else "")

    with st.spinner("IR Prohori is thinking..."):
        chunks = retrieve(query, k=3)
        answer = generate_answer(query, chunks)

    current_chat["messages"].append({"role": "assistant", "content": answer})
    st.rerun()