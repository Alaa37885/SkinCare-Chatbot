from langchain_groq import ChatGroq
from core.config import Config


def build_llm():

    return ChatGroq(
        model=Config.MODEL_NAME,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS
    )

