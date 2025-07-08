from typing import Dict, List
from datetime import datetime
import uuid
from schema.lim import LogEntry


class LogManager:
    def __init__(self):
        self.logs: Dict[str, LogEntry] = {}
    
    def create_log_entry(self, request_body: dict, response_body: dict, 
                        processing_time_ms: float, status: str) -> LogEntry:
        log_id = str(uuid.uuid4())
        log_entry = LogEntry(
            id=log_id,
            timestamp=datetime.now(),
            request_body=request_body,
            response_body=response_body,
            processing_time_ms=processing_time_ms,
            status=status
        )
        self.logs[log_id] = log_entry
        return log_entry
    
    def get_all_logs(self) -> List[LogEntry]:
        return sorted(list(self.logs.values()), key=lambda x: x.timestamp, reverse=True)
    
    def get_log(self, log_id: str) -> LogEntry:
        return self.logs.get(log_id)
    
    def clear_logs(self) -> int:
        count = len(self.logs)
        self.logs.clear()
        return count


def get_meeting_minutes_prompt() -> str:
    """Teams会議議事録生成用のプロンプトを返す"""
    return """あなたは経験豊富な会議議事録作成の専門家です。以下のTeams会議のトランスクリプトを分析し、構造化された議事録を作成してください。

必ず以下の形式で出力してください：

会議の目的と主要なテーマを2-3文で簡潔にまとめてください。参加者の主な役割や立場があれば記載し、会議の全体的な流れや結論を要約してください。

• 議論された重要な論点を箇条書きで記載
• 各参加者の主要な発言や意見を整理
• 提起された課題や問題点を明確に記述
• 数値やデータがあれば具体的に記載

• 具体的な行動項目を明確に記載
• 可能な限り担当者と期限を特定
• 優先度や重要度があれば記載
• 次回までに完了すべき事項を整理

• 会議で正式に決定された事項を明確に記載
• 承認された提案や方針を具体的に記述
• 今後の方向性や戦略について決定された内容
• 予算や人員配置などの具体的な決定事項

重要な注意事項：
- 各セクションは必ず「## セクション名」で始めてください
- 情報が不足している場合は「情報不足のため詳細不明」と記載
- 推測や憶測は避け、トランスクリプトに基づいた内容のみ記載
- 日本語で自然で読みやすい文章で作成してください

以下がトランスクリプトです：
"""


log_manager = LogManager()
