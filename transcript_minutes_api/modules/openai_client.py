from openai import AsyncOpenAI
import os
from typing import Optional
from dotenv import load_dotenv
from modules.logger import logger

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def get_openai_client():
    if not OPENAI_API_KEY or OPENAI_API_KEY == "test-key-placeholder":
        return None
    return AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_meeting_minutes(transcript: str, meeting_title: Optional[str] = None, participants: Optional[list] = None) -> str:
    try:
        client = get_openai_client()
        if not client:
            logger.error("OpenAI API key not configured or is placeholder")
            raise Exception("OpenAI API key not configured properly")
            
        prompt = f"""以下のトランスクリプトから議事録を作成してください。

【要求事項】
- 参加者の発言を整理
- 主要な議題と決定事項を明確化
- アクションアイテムの抽出
- 日本語で出力

【会議情報】
- タイトル: {meeting_title or "未指定"}
- 参加者: {", ".join(participants) if participants else "未指定"}

【トランスクリプト】
{transcript}

【議事録形式】

- 日時: [自動生成時刻]
- タイトル: {meeting_title or "未指定"}
- 参加者: {", ".join(participants) if participants else "未指定"}

[主要な議題と討議内容を整理]

[会議で決定された事項]

[今後のアクション項目と担当者]

[その他の重要事項]
"""

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "あなたは議事録作成の専門家です。与えられたトランスクリプトから構造化された議事録を作成してください。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        meeting_minutes = response.choices[0].message.content
        logger.info(f"Meeting minutes generated successfully. Length: {len(meeting_minutes)} characters")
        return meeting_minutes
        
    except Exception as e:
        logger.error(f"Error generating meeting minutes: {str(e)}")
        raise Exception(f"議事録生成中にエラーが発生しました: {str(e)}")
