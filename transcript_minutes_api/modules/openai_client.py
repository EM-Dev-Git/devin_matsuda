from openai import AsyncOpenAI
import os
from typing import List
from dotenv import load_dotenv
from .logger import logger

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

class OpenAIClient:
    def __init__(self):
        self.model = OPENAI_MODEL
        self.client = None
    
    def _get_client(self):
        if self.client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self.client = AsyncOpenAI(api_key=api_key)
        return self.client
    
    async def generate_minutes(self, transcript: str, meeting_title: str = "", participants: List[str] = None) -> str:
        try:
            participants_str = ", ".join(participants) if participants else "不明"
            
            prompt = f"""あなたは議事録作成の専門家です。以下のトランスクリプトから構造化された議事録を作成してください。

【トランスクリプト】
{transcript}

【会議情報】
- タイトル: {meeting_title}
- 参加者: {participants_str}

【出力形式】
1. 会議概要
2. 主要な議題
3. 決定事項
4. アクションアイテム
5. 次回までの課題

日本語で出力してください。"""

            logger.info(f"Generating minutes for meeting: {meeting_title}")
            
            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは議事録作成の専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            minutes = response.choices[0].message.content.strip()
            logger.info("Successfully generated meeting minutes")
            return minutes
            
        except Exception as e:
            logger.error(f"Error generating minutes: {str(e)}")
            raise Exception(f"議事録生成に失敗しました: {str(e)}")

openai_client = OpenAIClient()
