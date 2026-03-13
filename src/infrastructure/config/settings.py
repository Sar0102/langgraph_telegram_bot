

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    elevenlabs_api_key: str = Field(alias="ELEVENLABS_API_KEY")
    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")

    openai_chat_model: str = Field(default="gpt-4o-mini", alias="OPENAI_CHAT_MODEL")
    openai_image_model: str = Field(default="gpt-image-1", alias="OPENAI_IMAGE_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )
    openai_vision_model: str = Field(default="gpt-4o-mini", alias="OPENAI_VISION_MODEL")
    openai_transcription_model: str = Field(
        default="whisper-1", alias="OPENAI_TRANSCRIPTION_MODEL"
    )
    elevenlabs_voice_id: str = Field(alias="ELEVENLABS_VOICE_ID")
    elevenlabs_model_id: str = Field(alias="ELEVENLABS_MODEL_ID")

    bot_name: str = Field(default="Karan", alias="BOT_NAME")
    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    short_term_memory_path: Path = Field(
        default=Path("data/short-term-memory.db"), alias="SHORT_TERM_MEMORY_PATH"
    )
    vector_store_dir: Path = Field(default=Path("data/long-term-memory"), alias="VECTOR_STORE_DIR")
    biography_pdf_path: Path = Field(
        default=Path("data/vladimir_biography.pdf"), alias="BIOGRAPHY_PDF_PATH"
    )
    media_dir: Path = Field(default=Path("data/generated-media"), alias="MEDIA_DIR")
    vector_collection_name: str = Field(
        default="vladimir_biography_collection", alias="VECTOR_COLLECTION_NAME"
    )
    summary_message_threshold: int = Field(default=30, alias="SUMMARY_MESSAGE_THRESHOLD")
    retriever_k: int = Field(default=3, alias="RETRIEVER_K")
    image_size: str = Field(default="1024x1024", alias="IMAGE_SIZE")
    image_quality: str = Field(default="low", alias="IMAGE_QUALITY")

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.short_term_memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
