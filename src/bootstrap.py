from src.application.services.conversation_graph import ConversationGraphFactory
from src.application.services.telegram_gateway import GraphGateway
from src.infrastructure.ai.clients import AIClients
from src.infrastructure.config.settings import Settings
from src.infrastructure.media.service import MediaService
from src.infrastructure.memory.checkpointer import build_checkpointer
from src.infrastructure.rag.biography_retriever import BiographyRetrieverFactory
from src.interfaces.telegram.bot import TelegramBot
from src.interfaces.telegram.handlers import TelegramHandlers


def bootstrap() -> TelegramBot:
    settings = Settings()
    settings.ensure_directories()

    clients = AIClients(settings)
    retriever_tool = BiographyRetrieverFactory(
        settings=settings,
        embeddings=clients.embeddings,
    ).create_tool()
    media_service = MediaService(
        settings=settings,
        openai_client=clients.openai,
        elevenlabs_client=clients.elevenlabs,
    )
    graph = ConversationGraphFactory(
        llm=clients.chat_llm,
        retriever_tool=retriever_tool,
        media_service=media_service,
        checkpointer=build_checkpointer(settings),
        summary_threshold=settings.summary_message_threshold,
    ).create()
    handlers = TelegramHandlers(
        graph_gateway=GraphGateway(graph),
        openai_client=clients.openai,
        settings=settings,
    )
    return TelegramBot(
        token=settings.telegram_bot_token,
        handlers=handlers,
        bot_name=settings.bot_name,
    )
