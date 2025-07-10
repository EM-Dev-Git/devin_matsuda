from openai import OpenAI
from typing import Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.credentials_available = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.client = None
                self.credentials_available = False
                logger.error(f"OpenAI client initialization failed: {e}")
                print("Running in demo mode - OpenAI credentials not available.")
        else:
            self.client = None
            self.credentials_available = False
            logger.info("OpenAI API key not configured. Running in demo mode.")
            print("OpenAI API key not found. Running in demo mode.")
    
    async def generate_completion(self, system_prompt: str, user_message: str) -> str:
        if not self.credentials_available:
            return self._generate_demo_response(user_message)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            logger.info("OpenAI completion generated successfully")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            error_msg = f"OpenAI APIエラーが発生しました: {str(e)}\n\nエラーが発生しました。システム管理者に連絡してください。"
            return error_msg
    
    def _generate_demo_response(self, transcript: str) -> str:
        lines = transcript.split('\n')
        participants = set()
        topics = []
        
        for line in lines:
            line = line.strip()
            if ':' in line and len(line.split(':')[0]) < 50:
                speaker = line.split(':')[0].strip()
                if speaker and len(speaker) < 30:
                    participants.add(speaker)
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['プロジェクト', 'タスク', '課題', '問題', '提案', '決定', '承認']):
                if len(line) > 20 and len(line) < 200:
                    topics.append(line.strip())
        
        participant_list = list(participants)[:5]
        
        demo_minutes = f"""## 会議概要
【デモモード - 実際のトランスクリプト分析】

参加者: {', '.join(participant_list) if participant_list else '不明'}
トランスクリプト文字数: {len(transcript)}文字

主要な議論内容が含まれた会議のようです。実際のOpenAI APIを使用することで、より詳細で正確な議事録を生成できます。

• 参加者数: {len(participant_list)}名
• トランスクリプト総文字数: {len(transcript)}文字
• 検出されたトピック数: {len(topics)}件
• 実際のAI分析により、より詳細な議論内容を抽出可能

• OpenAI API認証情報の設定
• 実際の会議トランスクリプトでの本格テスト
• 議事録生成精度の確認と調整

• デモモードでの基本動作確認完了
• トランスクリプト解析機能の実装確認
• 本格運用に向けたAPI設定が必要"""

        logger.info("Demo meeting minutes generated successfully")
        return demo_minutes

openai_client = OpenAIClient()
