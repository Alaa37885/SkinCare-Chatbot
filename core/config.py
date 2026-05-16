import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("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")


class Config:

    MODEL_NAME = os.getenv("MODEL_NAME")
    TEMPERATURE = float(os.getenv("TEMPERATURE"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS"))

