import base64

from openai import AsyncOpenAI
import json
from infrastructure.config.settings import get_settings


settings = get_settings()


class OpenAIRepository:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe_audio(self, audio_file_path: str) -> str:
        audio_file = open(audio_file_path, "rb")
        transcription = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text

    async def get_json_response(self, prompt: str) -> dict:
        response = await self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        content = response.choices[0].message.content
        if content:
            return json.loads(content)
        return {}

    async def get_photo_and_text_json_response(self, prompt: str, image_file_path: str) -> dict:
        with open(image_file_path, "rb") as image_file:
            image_data = image_file.read()

        image_b64 = base64.b64encode(image_data).decode("utf-8")
        mime_type = "image/jpeg"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}"
                        }
                    }
                ]
            }
        ]

        response =  await self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            max_tokens=1000
        )

        content = response.choices[0].message.content
        if content:
            return json.loads(content)
        return {}
