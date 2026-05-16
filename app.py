import os
import time
import random
import threading
from resolver.shortcuts import SHORTCUT_REGISTRY
from resolver.resolver import resolve_shortcut
from collections import deque

import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from pypdf import PdfReader
from langchain.prompts import PromptTemplate


# =========================
# LOAD ENV
# =========================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =========================
# RATE LIMITER
# =========================
class RPMRateLimiter:

    def __init__(self, rpm=30, window_s=60):
        self.rpm = rpm
        self.window_s = window_s
        self.requests = deque()
        self.lock = threading.Lock()

    def cleanup(self):
        cutoff = time.time() - self.window_s
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

    def acquire(self):
        while True:
            with self.lock:
                self.cleanup()
                if len(self.requests) < self.rpm:
                    self.requests.append(time.time())
                    return True
            time.sleep(0.5)


rate_limiter = RPMRateLimiter(rpm=30)


# =========================
# PDF
# =========================
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


# =========================
# EVALUATION
# =========================
def evaluate_response(response):
    return {
        "characters": len(response),
        "words": len(response.split()),
        "is_empty": len(response.strip()) == 0
    }


# =========================
# RETRY
# =========================
def invoke_with_retry(conversation, user_input, max_attempts=5):

    for attempt in range(max_attempts):

        try:
            return conversation.predict(input=user_input)

        except Exception as e:

            status_code = getattr(e, "status_code", None)
            retryable = [429, 500, 502, 503, 504]

            if status_code not in retryable:
                raise e

            delay = min(2 ** attempt, 60)
            jitter = random.uniform(0, 0.5)
            time.sleep(delay + jitter)

    raise Exception("Max retries exceeded")


# =========================
# STREAMLIT APP
# =========================
def main():

    st.set_page_config(
        page_title="SkinCare Assistant",
        page_icon="🌸",
        layout="wide"
    )

    # =========================
    # BACKGROUND (NEW - NO FILES NEEDED)
    # =========================
    st.markdown("""
    <style>

    /* ================= BACKGROUND ================= */
    .stApp {
        background:
            linear-gradient(
                rgba(255, 255, 255, 0.82),
                rgba(255, 245, 250, 0.88)
            ),
            url("https://images.unsplash.com/photo-1596755389378-c31d21fd1273");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    /* ================= GLASS CONTAINER ================= */
    .block-container {
        background: rgba(255, 255, 255, 0.80);
        padding: 2rem;
        border-radius: 25px;
        backdrop-filter: blur(20px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.10);
    }

    /* ================= TITLE ================= */
    h1 {
        color: #b85c7a !important;
        text-align: center;
        font-size: 42px !important;
        font-weight: 600;
        text-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }

    /* ================= BUTTONS (SOFT PINK) ================= */
    .stButton > button {
        background: #f3c6d4;   /* soft pink */
        color: #5a2a3a;        /* dark muted text */
        border: none;
        border-radius: 14px;
        padding: 10px 20px;
        font-weight: 600;
        transition: 0.25s ease;
    }

    .stButton > button:hover {
        background: #eab7c8;   /* slightly darker on hover */
        transform: scale(1.03);
    }

    /* ================= TEXTBOX ================= */
    .stTextArea textarea {
        border-radius: 15px;
        border: 2px solid #f1c1cf !important;
        background: rgba(255,255,255,0.95);
    }

    /* ================= SIDEBAR ================= */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(20px);
    }

    </style>
    """, unsafe_allow_html=True)

    st.title("🌸 SkinCare Assistant")

    # =========================
    # SESSION STATE
    # =========================
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.title("⚙ Settings")

    model = st.sidebar.selectbox(
        "Choose a model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it"
        ]
    )

    memory_len = st.sidebar.slider(
        "Memory Length",
        1, 10, value=5
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )


    # =========================
    # SHORTCUT BUTTONS
    # =========================
    st.subheader("⚡ Quick Shortcuts")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("🧴 Routine"):
        st.session_state.input_text = "/ i want a routine for ..."

    if col2.button("🧪 Ingredient"):
        st.session_state.input_text = "/i want to know about a specific ingredient ..."

    if col3.button("😤 Acne"):
        st.session_state.input_text = "/i have acne ..."

    if col4.button("🛡 Safe"):
        st.session_state.input_text = "/ i want to know about safe ingredients ..."
    # =========================
    # INPUT BOX (ONLY CHANGE HERE)
    # =========================
    user_question = st.text_area(
        "Ask your skincare question",
        value=st.session_state.input_text
    )


    # =========================
    # MEMORY
    # =========================
    memory = ConversationBufferMemory(
        k=memory_len,
        return_messages=True
    )

    for msg in st.session_state.chat_history:
        memory.save_context(
            {"input": msg["human"]},
            {"output": msg["AI"]}
        )


    # =========================
    # MODEL
    # =========================
    groq_chat = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=model,
        temperature=0.3,
        max_tokens=1024
    )


    template = """
    You are a skincare assistant.

    Detect language and reply in same language.
    Only skincare questions.

    If unrelated:
    Arabic: أنا أساعد فقط في العناية بالبشرة.
    English: I can only help with skincare-related questions.

    History:
    {history}

    Human: {input}
    AI:
    """

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=template
    )

    conversation = ConversationChain(
        llm=groq_chat,
        memory=memory,
        prompt=prompt
    )


    # =========================
    # PDF
    # =========================
    extracted_text = ""

    if uploaded_file:
        extracted_text = extract_text_from_pdf(uploaded_file)
        st.sidebar.success("PDF loaded")


    # =========================
    # SEND
    # =========================
    if st.button("Send"):

        if not user_question.strip():
            st.warning("Enter a question")
            return

        rate_limiter.acquire()

        resolved = resolve_shortcut(
            user_question,
            SHORTCUT_REGISTRY
        )

        final_input = resolved.prompt

        if extracted_text:
            final_input += "\n\nPDF Context:\n" + extracted_text[:4000]

        with st.spinner("Thinking..."):
            response = invoke_with_retry(
                conversation,
                final_input
            )

        st.session_state.chat_history.append({
            "human": user_question,
            "AI": response
        })

        # reset input ⭐
        st.session_state.input_text = ""

        st.subheader("💖 Response")
        st.write(response)

        st.subheader("📊 Evaluation")
        st.json(evaluate_response(response))

        wait_for_all_tracers()


    # =========================
    # HISTORY
    # =========================
    if st.session_state.chat_history:

        st.subheader("🕒 Chat History")

        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**You:** {chat['human']}")
            st.markdown(f"**Bot:** {chat['AI']}")
            st.write("---")


if __name__ == "__main__":
    main()