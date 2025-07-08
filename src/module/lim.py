from openai import AzureOpenAI
from typing import Dict
from config import settings
from datetime import datetime


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
    
    def _get_meeting_minutes_prompt(self) -> str:
        return """
あなたは会議の議事録作成の専門家です。以下のTeams会議のトランスクリプトから、構造化された議事録を作成してください。

以下の形式で出力してください：

[会議の全体的な概要を2-3文で記述]

[重要な議論点や決定事項を箇条書きで記述]

[具体的な行動項目、担当者、期限があれば記述]

[会議で決定された事項を明確に記述]

トランスクリプト:
"""
    
    async def generate_meeting_minutes(self, transcript: str, meeting_title: str = None, 
                                     meeting_date: str = None, participants: str = None) -> Dict[str, str]:
        if not self.credentials_available:
            return {
                "summary": f"【デモモード】会議議事録生成システムのデモです。\n\n会議タイトル: {meeting_title or '未設定'}\n会議日時: {meeting_date or '未設定'}\n参加者: {participants or '未設定'}\n\nトランスクリプト文字数: {len(transcript)}文字\n\n実際のAI生成議事録を取得するには、env/.envファイルにAzure OpenAI認証情報を設定してください。",
                "key_points": "• デモモードで動作中\n• Azure OpenAI認証情報が必要\n• トランスクリプト処理機能は実装済み",
                "action_items": "• Azure OpenAI APIキーの設定\n• 実際の会議トランスクリプトでのテスト",
                "decisions": "• デモモードでの動作確認完了\n• システムの基本機能は正常"
            }
        
        try:
            prompt = self._get_meeting_minutes_prompt()
            
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
            if '## 会議概要' in line or '概要' in line:
                current_section = "summary"
            elif '## 主要なポイント' in line or 'ポイント' in line:
                current_section = "key_points"
            elif '## アクションアイテム' in line or 'アクション' in line:
                current_section = "action_items"
            elif '## 決定事項' in line or '決定' in line:
                current_section = "decisions"
            elif line and current_section and not line.startswith('#'):
                if sections[current_section]:
                    sections[current_section] += "\n" + line
                else:
                    sections[current_section] = line
        
        for key in sections:
            if not sections[key]:
                sections[key] = "該当なし"
        
        return sections


meeting_minutes_generator = MeetingMinutesGenerator()
