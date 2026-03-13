

from elevenlabs import ElevenLabs
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import OpenAI

from src.infrastructure.config.settings import Settings


class AIClients:
    def __init__(self, settings: Settings) -> None:
        self.chat_llm = ChatOpenAI(
            model=settings.openai_chat_model,
            temperature=0,
            api_key=settings.openai_api_key,
        )
        self.openai = OpenAI(api_key=settings.openai_api_key)
        self.elevenlabs = ElevenLabs(api_key=settings.elevenlabs_api_key)
        self.embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )
