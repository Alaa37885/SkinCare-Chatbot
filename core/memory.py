
"""
from langchain.memory import ConversationBufferWindowMemory


def build_memory():

    return ConversationBufferWindowMemory(
        k=10,
        return_messages=True,
        memory_key="chat_history",
        input_key="input",
        output_key="output"
    )

"""


from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel, Field
from uuid import uuid4
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser


# =========================
# CONFIG (UNIFIED)
# =========================
class AgentConfig(BaseModel):
    memory_window_k: int = Field(default=10, ge=1, le=50)
    rpm_limit: int = Field(default=30)


# =========================
# MEMORY BUILDER
# =========================
def build_memory(k: int = 10) -> ConversationBufferWindowMemory:
    return ConversationBufferWindowMemory(
        k=k,
        return_messages=True,
        memory_key="chat_history",
        input_key="input",
        output_key="output",
    )


# =========================
# AGENT
# =========================
class AgentOrchestrator:

    def __init__(self, config: AgentConfig, llm, prompt):

        self.config = config
        self.llm = llm
        self.prompt = prompt

        # Memory
        self.memory = build_memory(config.memory_window_k)

        # Session ID
        self.session_id = str(uuid4())

        # Load Memory
        self.load_memory = RunnableLambda(
            lambda x: {
                **x,
                "chat_history": self.memory.load_memory_variables({})["chat_history"]
            }
        )

        # Chain
        self.chain = (
            self.load_memory
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    # =========================
    # RESET SESSION
    # =========================
    def reset_session(self):
        self.memory.clear()
        self.session_id = str(uuid4())
        print(f"🔄 Memory cleared. New Session ID: {self.session_id}")

    # =========================
    # SAVE MEMORY
    # =========================
    def save_chat(self, user_input, bot_output):
        self.memory.save_context(
            {"input": user_input},
            {"output": bot_output}
        )
        print("✅ Conversation Saved To Memory")