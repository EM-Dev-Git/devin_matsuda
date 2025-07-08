from openai import AzureOpenAI
from typing import Dict
from config import settings
from datetime import datetime
from module.prompt import get_meeting_minutes_prompt


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
            except Exception as e:
                self.client = None
                self.credentials_available = False
                print(f"Azure OpenAI client initialization failed: {e}")
                print("Running in demo mode.")
        else:
            self.client = None
            self.credentials_available = False
            print("Azure OpenAI credentials not found. Running in demo mode.")
    
    
    async def generate_meeting_minutes(self, transcript: str) -> Dict[str, str]:
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
            
            sections = self._parse_meeting_minutes(content)
            return sections
            
        except Exception as e:
            error_msg = f"Azure OpenAI APIエラーが発生しました: {str(e)}"
            return {
                "summary": error_msg,
                "key_points": "エラーが発生しました",
                "action_items": "システム管理者に連絡してください",
                "decisions": "処理を完了できませんでした"
            }
    
    def _parse_meeting_minutes(self, content: str) -> Dict[str, str]:
        sections = {
            "summary": "",
            "key_points": "",
            "action_items": "",
            "decisions": ""
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('## 会議概要') or line.startswith('### ## 会議概要'):
                current_section = "summary"
                continue
            elif line.startswith('## 主要なポイント') or line.startswith('### ## 主要なポイント'):
                current_section = "key_points"
                continue
            elif line.startswith('## アクションアイテム') or line.startswith('### ## アクションアイテム'):
                current_section = "action_items"
                continue
            elif line.startswith('## 決定事項') or line.startswith('### ## 決定事項'):
                current_section = "decisions"
                continue
            
            if line and current_section and not line.startswith('#'):
                if sections[current_section]:
                    sections[current_section] += "\n" + line
                else:
                    sections[current_section] = line
        
        for key in sections:
            if not sections[key].strip():
                sections[key] = "該当する情報がトランスクリプトに含まれていません"
        
        return sections
    
    def _generate_demo_minutes(self, transcript: str) -> Dict[str, str]:
        """デモモード用の議事録生成（実際のトランスクリプト内容を分析）"""
        
        lines = transcript.split('\n')
        participants = set()
        topics = []
        
        for line in lines:
            line = line.strip()
            if ':' in line and len(line.split(':')[0]) < 50:
                speaker = line.split(':')[0].strip()
                if speaker and len(speaker) < 30:
                    participants.add(speaker)
            
            if any(keyword in line.lower() for keyword in ['プロジェクト', 'タスク', '課題', '問題', '提案', '決定', '承認']):
                if len(line) > 20 and len(line) < 200:
                    topics.append(line.strip())
        
        participant_list = list(participants)[:5]  # 最大5名まで
        
        return {
            "summary": f"【デモモード - 実際のトランスクリプト分析】\n\n参加者: {', '.join(participant_list) if participant_list else '不明'}\nトランスクリプト文字数: {len(transcript)}文字\n\n主要な議論内容が含まれた会議のようです。実際のAzure OpenAI APIを使用することで、より詳細で正確な議事録を生成できます。",
            
            "key_points": f"• 参加者数: {len(participant_list)}名\n• トランスクリプト総文字数: {len(transcript)}文字\n• 検出されたトピック数: {len(topics)}件\n• 実際のAI分析により、より詳細な議論内容を抽出可能",
            
            "action_items": "• Azure OpenAI API認証情報の設定\n• 実際の会議トランスクリプトでの本格テスト\n• 議事録生成精度の確認と調整",
            
            "decisions": "• デモモードでの基本動作確認完了\n• トランスクリプト解析機能の実装確認\n• 本格運用に向けたAPI設定が必要"
        }


meeting_minutes_generator = MeetingMinutesGenerator()
