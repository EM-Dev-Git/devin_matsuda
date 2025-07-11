
from modules.openai_client import openai_client  # OpenAI APIクライアント（シングルトンインスタンス）
from modules.logger import api_logger  # API専用ロガー（リクエスト・レスポンス・エラーログ記録用）
from datetime import datetime  # 日時操作（処理時間計測用）
import logging  # 標準ログライブラリ

logger = logging.getLogger(__name__)

class MinutesGenerator:
    """
    議事録生成クラス
    Teams会議のトランスクリプトを受け取り、OpenAI GPTモデルを使用して
    構造化された議事録を生成するクラスです
    
    主な機能：
    - トランスクリプトの前処理とバリデーション
    - OpenAI APIを使用した議事録生成
    - 処理時間の計測とログ記録
    - エラーハンドリングと例外処理
    - システムプロンプトの管理
    
    使用例：
        generator = MinutesGenerator()
        minutes = await generator.generate_meeting_minutes(transcript, user_id)
    
    依存関係：
    - modules.openai_client: OpenAI API通信
    - modules.logger: 構造化ログ記録
    """
    
    def __init__(self):
        """
        議事録生成クラスの初期化
        
        OpenAIクライアントのシングルトンインスタンスを取得し、
        議事録生成の準備を行います。
        
        初期化内容：
        - OpenAIクライアントインスタンスの参照取得
        - 必要な依存関係の確認
        """
        self.openai_client = openai_client
    
    async def generate_meeting_minutes(self, transcript: str, user_id: str = None) -> str:
        """
        Teams会議のトランスクリプトから議事録を生成する
        
        この関数は議事録生成の中核となる処理を実行します：
        1. リクエストログの記録
        2. システムプロンプトの取得
        3. OpenAI APIを使用した議事録生成
        4. 処理時間の計測
        5. レスポンスログの記録
        6. エラーハンドリング
        
        Args:
            transcript (str): Teams会議のトランスクリプト（発言者名と発言内容を含む）
            user_id (str, optional): 議事録生成を要求したユーザーID（ログ記録用）
            
        Returns:
            str: 生成された議事録（Markdown形式の構造化テキスト）
            
        Raises:
            Exception: 議事録生成中にエラーが発生した場合
            
        処理フロー：
        1. APIリクエストログ記録（トランスクリプト文字数含む）
        2. 議事録生成用システムプロンプト取得
        3. 処理開始時刻記録
        4. OpenAI API呼び出し（GPTモデルによる議事録生成）
        5. 処理終了時刻記録・処理時間計算
        6. APIレスポンスログ記録（生成された議事録文字数・処理時間含む）
        7. 成功ログ出力・議事録返却
        
        エラー処理：
        - OpenAI API呼び出し失敗
        - ネットワーク接続エラー
        - レート制限エラー
        - 認証エラー
        - その他の予期しないエラー
        
        使用例:
            minutes = await generator.generate_meeting_minutes(
                "山田: おはようございます。今日は...",
                "user123"
            )
        """
        try:
            api_logger.log_request(
                endpoint="/minutes/generate",                    # エンドポイント名
                method="POST",                                   # HTTPメソッド
                user_id=user_id,                                # リクエスト送信ユーザーID
                request_body={"transcript_length": len(transcript)}  # トランスクリプト文字数（機密情報除外）
            )
            
            system_prompt = self._get_meeting_minutes_prompt()
            
            start_time = datetime.utcnow()
            
            meeting_minutes = await self.openai_client.generate_completion(
                system_prompt=system_prompt,  # AIの役割と出力形式の指示
                user_message=transcript       # Teams会議のトランスクリプト
            )
            
            end_time = datetime.utcnow()
            
            processing_time = (end_time - start_time).total_seconds()
            
            api_logger.log_response(
                endpoint="/minutes/generate",                    # エンドポイント名
                method="POST",                                   # HTTPメソッド
                status_code=200,                                 # HTTPステータスコード（成功）
                user_id=user_id,                                # レスポンス対象ユーザーID
                response_body={"minutes_length": len(meeting_minutes)},  # 生成された議事録文字数
                processing_time=processing_time                  # 処理時間（秒）
            )
            
            logger.info(f"Meeting minutes generated successfully for user: {user_id}")
            
            return meeting_minutes
            
        except Exception as e:
            
            error_msg = f"議事録生成中にエラーが発生しました: {str(e)}"
            
            api_logger.log_error(
                endpoint="/minutes/generate",  # エラー発生エンドポイント
                method="POST",                 # HTTPメソッド
                error=error_msg,              # エラーメッセージ
                user_id=user_id               # エラー発生ユーザーID
            )
            
            logger.error(f"Error generating meeting minutes: {str(e)}")
            
            raise Exception(error_msg)
    
    def _get_meeting_minutes_prompt(self) -> str:
        """
        議事録生成用のシステムプロンプトを取得する
        
        OpenAI GPTモデルに送信するシステムプロンプトを定義します。
        このプロンプトはAIの役割、出力形式、注意事項を詳細に指定し、
        一貫性のある高品質な議事録生成を実現します。
        
        Returns:
            str: 議事録生成用のシステムプロンプト（日本語）
            
        プロンプト構成要素：
        1. AIの役割定義（会議議事録作成の専門家）
        2. 入力データの説明（Teams会議トランスクリプト）
        3. 出力形式の詳細指定（構造化された議事録形式）
        4. 各セクションの内容説明
        5. 品質要件と注意事項
        
        出力形式：
        - 会議基本情報（日時、参加者、目的）
        - 議論内容（重要トピックの整理）
        - 決定事項（合意内容、承認事項）
        - アクションアイテム（担当者、期限、フォローアップ）
        - 次回予定（該当する場合）
        
        品質要件：
        - 日本語での出力
        - 重要情報の漏れ防止
        - 発言者意図の正確な反映
        - 専門用語の適切な使用
        
        使用例:
            prompt = self._get_meeting_minutes_prompt()
        """
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
