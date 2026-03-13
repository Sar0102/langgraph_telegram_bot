

import base64
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from langchain_core.messages import RemoveMessage
from PIL import Image

from src.domain.prompts import BASIC_IMAGE_PROMPT
from src.infrastructure.config.settings import Settings


class MediaService:
    def __init__(self, *, settings: Settings, openai_client, elevenlabs_client) -> None:
        self._settings = settings
        self._openai_client = openai_client
        self._elevenlabs_client = elevenlabs_client

    def generate_audio(self, text: str) -> bytes:
        audio = self._elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=self._settings.elevenlabs_voice_id,
            model_id=self._settings.elevenlabs_model_id,
        )
        return b"".join(audio)

    def generate_image(self, context: str) -> str:
        result = self._openai_client.images.generate(
            model=self._settings.openai_image_model,
            prompt=f"{BASIC_IMAGE_PROMPT}\n{context}",
            quality=self._settings.image_quality,
            size=self._settings.image_size,
        )
        image_bytes = base64.b64decode(result.data[0].b64_json)
        image = Image.open(BytesIO(image_bytes))
        image_path = self._settings.media_dir / f"{uuid4()}.png"
        image.save(image_path)
        return str(image_path)

    @staticmethod
    def make_remove_messages(messages) -> list[RemoveMessage]:
        return [RemoveMessage(id=message.id) for message in messages]
