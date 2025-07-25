import openai
from typing import Optional
from ..config import settings
from .logger import get_logger

logger = get_logger(__name__)

MEETING_MINUTES_PROMPT = """
以下のトランスクリプトから議事録を作成してください。

要求事項:
1. 会議の概要
2. 主要な議論ポイント
3. 決定事項
4. アクションアイテム（担当者・期限含む）
5. 次回会議の予定

トランスクリプト:
{transcript}

議事録:
"""


class OpenAIClient:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.model = settings.openai_model

    async def generate_meeting_minutes(self, transcript: str) -> Optional[str]:
        try:
            logger.info("Starting meeting minutes generation", extra={"transcript_length": len(transcript)})
            
            prompt = MEETING_MINUTES_PROMPT.format(transcript=transcript)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            generated_minutes = response.choices[0].message.content.strip()
            logger.info("Meeting minutes generated successfully", extra={"minutes_length": len(generated_minutes)})
            
            return generated_minutes
            
        except Exception as e:
            logger.error("Failed to generate meeting minutes", extra={"error": str(e)})
            return None


openai_client = OpenAIClient()
