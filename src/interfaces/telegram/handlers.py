

import base64
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from telegram import Update
from telegram.ext import ContextTypes


class TelegramHandlers:
    def __init__(self, *, graph_gateway, openai_client, settings) -> None:
        self._graph_gateway = graph_gateway
        self._openai_client = openai_client
        self._settings = settings

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.effective_user:
            return
        response = self._graph_gateway.invoke(
            user_id=str(update.effective_user.id),
            message=update.message.text,
        )
        await self._send_response(update, context, response)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.effective_user or not update.message.photo:
            return
        photo = update.message.photo[-1]
        telegram_file = await context.bot.get_file(photo.file_id)
        temp_path = self._settings.media_dir / f"{uuid4()}-incoming-photo.jpg"
        await telegram_file.download_to_drive(str(temp_path))
        with temp_path.open("rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        temp_path.unlink(missing_ok=True)

        vision_response = self._openai_client.chat.completions.create(
            model=self._settings.openai_vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe what you see in the picture."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
        )
        description = vision_response.choices[0].message.content.strip()
        caption = update.message.caption or ""
        combined_message = f"{caption} [IMAGE_ANALYSIS] {description}".strip()
        response = self._graph_gateway.invoke(
            user_id=str(update.effective_user.id),
            message=combined_message,
        )
        await self._send_response(update, context, response)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.effective_user or not update.message.voice:
            return
        voice = update.message.voice
        telegram_file = await context.bot.get_file(voice.file_id)
        temp_path = self._settings.media_dir / f"{uuid4()}-incoming-voice.ogg"
        await telegram_file.download_to_drive(str(temp_path))
        with temp_path.open("rb") as audio_file:
            transcription = self._openai_client.audio.transcriptions.create(
                file=audio_file,
                model=self._settings.openai_transcription_model,
            )
        temp_path.unlink(missing_ok=True)
        response = self._graph_gateway.invoke(
            user_id=str(update.effective_user.id),
            message=transcription.text,
        )
        await self._send_response(update, context, response)

    async def _send_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response) -> None:
        if "image_path" in response:
            image_path = Path(response["image_path"])
            with image_path.open("rb") as image_file:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)
            return
        if "audio_buffer" in response:
            voice_stream = BytesIO(response["audio_buffer"])
            voice_stream.name = "reply.ogg"
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_stream)
            return
        message = response["messages"][-1].content
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
