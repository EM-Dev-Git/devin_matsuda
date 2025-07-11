
from pydantic import BaseModel  # Pydanticのベースモデルクラス（データ検証・シリアライゼーション用）
from datetime import datetime  # 日時型の定義

class MinutesRequest(BaseModel):
    """
    議事録生成リクエストのスキーマ
    Teams会議のトランスクリプトから議事録を生成する際にクライアントから送信されるデータの形式を定義します
    
    使用例:
    POST /minutes/generate
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    {
        "transcript": "山田: おはようございます。今日は新製品の開発スケジュールについて話し合いましょう。\n鈴木: はい、デザインの進捗はいかがですか？\n田中: デザインは80%完了しています。来週には完成予定です。"
    }
    
    このスキーマにより、以下の検証が自動的に行われます：
    - transcriptが文字列型であること
    - transcriptフィールドが必須であること（None値不可）
    - リクエストボディのJSON形式が正しいこと
    
    注意: このエンドポイントはJWT認証が必須です
    """
    transcript: str

class MinutesResponse(BaseModel):
    """
    議事録生成レスポンスのスキーマ
    OpenAIによって生成された議事録をクライアントに返す際のデータ形式を定義します
    
    使用例:
    POST /minutes/generate のレスポンス（成功時）
    {
        "meeting_minutes": "## 会議議事録\n\n**日時**: 2025年1月10日\n**参加者**: 山田、鈴木、田中\n\n### 議題\n- 新製品の開発スケジュール\n\n### 決定事項\n- デザインは来週完成予定\n- 実装フェーズは2月開始\n\n### アクションアイテム\n- 田中: デザイン完成 (来週まで)\n- 鈴木: 技術仕様書作成 (1月末まで)",
        "generated_at": "2025-01-10T08:30:45.123456Z"
    }
    
    生成された議事録は構造化されたMarkdown形式で返され、
    以下の要素を含みます：
    - 会議の基本情報（日時、参加者）
    - 議題・討議内容
    - 決定事項
    - アクションアイテム
    - 次回予定（該当する場合）
    """
    meeting_minutes: str
    
    generated_at: datetime
