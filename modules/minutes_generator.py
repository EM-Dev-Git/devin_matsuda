from modules.openai_client import openai_client
from modules.logger import api_logger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MinutesGenerator:
    def __init__(self):
        self.openai_client = openai_client
    
    async def generate_meeting_minutes(self, transcript: str, user_id: str = None) -> str:
        """トランスクリプトから議事録を生成"""
        try:
            api_logger.log_request(
                endpoint="/minutes/generate",
                method="POST",
                user_id=user_id,
                request_body={"transcript_length": len(transcript)}
            )
            
            system_prompt = self._get_meeting_minutes_prompt()
            
            start_time = datetime.utcnow()
            meeting_minutes = await self.openai_client.generate_completion(
                system_prompt=system_prompt,
                user_message=transcript
            )
            end_time = datetime.utcnow()
            
            processing_time = (end_time - start_time).total_seconds()
            
            api_logger.log_response(
                endpoint="/minutes/generate",
                method="POST",
                status_code=200,
                user_id=user_id,
                response_body={"minutes_length": len(meeting_minutes)},
                processing_time=processing_time
            )
            
            logger.info(f"Meeting minutes generated successfully for user: {user_id}")
            return meeting_minutes
            
        except Exception as e:
            error_msg = f"議事録生成中にエラーが発生しました: {str(e)}"
            api_logger.log_error(
                endpoint="/minutes/generate",
                method="POST",
                error=error_msg,
                user_id=user_id
            )
            logger.error(f"Error generating meeting minutes: {str(e)}")
            raise Exception(error_msg)
    
    def _get_meeting_minutes_prompt(self) -> str:
        """議事録生成用のシステムプロンプト"""
        return """あなたは会議の議事録を作成する専門家です。提供されたTeams会議のトランスクリプトから、構造化された議事録を作成してください。

以下の形式で議事録を作成してください：

- 日時: [トランスクリプトから推測できる場合]
- 参加者: [発言者名から抽出]
- 会議の目的: [内容から推測]

- [重要なトピックを箇条書きで整理]
- [各トピックについて簡潔にまとめる]

- [会議で決定された事項を明確に記載]
- [承認された内容や合意事項]

- [誰が何をいつまでに行うかを明記]
- [フォローアップが必要な事項]

- [次回の予定や議題があれば記載]

注意事項：
- 日本語で作成してください
- 重要な情報を漏らさないよう注意してください
- 発言者の意図を正確に反映してください
- 専門用語は適切に使用してください"""

minutes_generator = MinutesGenerator()
