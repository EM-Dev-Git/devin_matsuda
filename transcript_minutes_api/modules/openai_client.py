import openai
import os
from typing import List, Optional
from dotenv import load_dotenv
from modules.logger import logger

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

client = None
if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-your-"):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_meeting_minutes(
    transcript: str,
    meeting_title: Optional[str] = None,
    participants: Optional[List[str]] = None
) -> str:
    if not client:
        logger.error("OpenAI API key not configured properly")
        raise Exception("OpenAI API key not configured")
    
    participants_str = ", ".join(participants) if participants else "未指定"
    title_str = meeting_title if meeting_title else "会議"
    
    prompt = f"""あなたは議事録作成の専門家です。以下のトランスクリプトから構造化された議事録を作成してください。

【トランスクリプト】
{transcript}

【会議情報】
- タイトル: {title_str}
- 参加者: {participants_str}

【出力形式】
以下の形式で議事録を作成してください：


- 会議名: {title_str}
- 参加者: {participants_str}
- 日時: [トランスクリプトから推測または未指定]

[トランスクリプトから主要な議題を抽出]

[会議で決定された事項を箇条書きで]

[今後のアクション項目を担当者と期限付きで]

[次回会議までに検討・実施すべき事項]

[その他重要な情報や補足事項]"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "あなたは会議の議事録作成を専門とするアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        meeting_minutes = response.choices[0].message.content.strip()
        logger.info(f"Successfully generated meeting minutes using {OPENAI_MODEL}")
        return meeting_minutes
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise Exception(f"Failed to generate meeting minutes: {str(e)}")
