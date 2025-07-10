from openai import AzureOpenAI
from typing import Optional
from config import settings
from datetime import datetime
from module.prompt import get_meeting_minutes_prompt
import logging

logger = logging.getLogger(__name__)


class MeetingMinutesGenerator:
    def __init__(self):
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        
        if settings.azure_openai_configured:
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version="2024-02-01",
                    azure_endpoint=self.endpoint
                )
                self.credentials_available = True
                logger.info("Azure OpenAI client initialized successfully")
            except Exception as e:
                self.client = None
                self.credentials_available = False
                logger.error(f"Azure OpenAI client initialization failed: {e}")
                print("Running in demo mode.")
        else:
            self.client = None
            self.credentials_available = False
            logger.info("Azure OpenAI credentials not configured. Running in demo mode.")
            print("Azure OpenAI credentials not found. Running in demo mode.")
    
    async def generate_meeting_minutes(self, transcript: str) -> str:
        """トランスクリプトから議事録を生成"""
        if not self.credentials_available:
            return self._generate_demo_minutes(transcript)
        
        try:
            prompt = get_meeting_minutes_prompt()
            
            messages = [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            logger.info("Meeting minutes generated successfully using Azure OpenAI")
            return content
            
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {str(e)}")
            error_msg = f"Azure OpenAI APIエラーが発生しました: {str(e)}\n\nエラーが発生しました。システム管理者に連絡してください。\n処理を完了できませんでした。"
            return error_msg
    
    def _generate_demo_minutes(self, transcript: str) -> str:
        """デモモード用の議事録生成"""
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
        
        meeting_minutes = f"""## 会議概要
【デモモード - 実際のトランスクリプト分析】

参加者: {', '.join(participant_list) if participant_list else '不明'}
トランスクリプト文字数: {len(transcript)}文字

主要な議論内容が含まれた会議のようです。実際のAzure OpenAI APIを使用することで、より詳細で正確な議事録を生成できます。

• 参加者数: {len(participant_list)}名
• トランスクリプト総文字数: {len(transcript)}文字
• 検出されたトピック数: {len(topics)}件
• 実際のAI分析により、より詳細な議論内容を抽出可能

• Azure OpenAI API認証情報の設定
• 実際の会議トランスクリプトでの本格テスト
• 議事録生成精度の確認と調整

• デモモードでの基本動作確認完了
• トランスクリプト解析機能の実装確認
• 本格運用に向けたAPI設定が必要"""

        logger.info("Demo meeting minutes generated successfully")
        return meeting_minutes


meeting_minutes_generator = MeetingMinutesGenerator()
