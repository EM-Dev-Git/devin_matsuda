
import logging  # Pythonの標準ログライブラリ
import json  # JSON形式でのデータシリアライゼーション
from datetime import datetime  # 日時操作（タイムスタンプ生成用）
from typing import Any, Dict  # 型ヒント（辞書型とAny型）
import os  # 環境変数取得用
from dotenv import load_dotenv  # .envファイルから環境変数読み込み

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

class APILogger:
    """
    API専用ログ管理クラス
    FastAPI アプリケーションのリクエスト・レスポンス・エラー・認証試行を
    構造化されたJSON形式でコンソールに出力します
    
    主な機能：
    - リクエストログ（エンドポイント、メソッド、ユーザーID、リクエストボディ）
    - レスポンスログ（ステータスコード、レスポンスボディ、処理時間）
    - エラーログ（エラー内容、発生箇所）
    - 認証試行ログ（ログイン成功/失敗、IPアドレス）
    
    ログ形式：
    すべてのログはJSON形式で出力され、以下の共通フィールドを含みます：
    - type: ログの種類（REQUEST, RESPONSE, ERROR, AUTH_ATTEMPT）
    - timestamp: ISO 8601形式のタイムスタンプ（UTC）
    - その他の種類別固有フィールド
    
    使用例：
        api_logger.log_request("/auth/login", "POST", "user123", {"user_id": "user123"})
    """
    
    def __init__(self):
        """
        APIロガーの初期化
        
        コンソール出力用のログハンドラーを設定し、JSON形式でのログ出力を準備します。
        ログレベルは環境変数LOG_LEVELで制御可能です。
        
        設定内容：
        - ロガー名：api_logger
        - 出力先：コンソール（標準出力）
        - フォーマット：タイムスタンプ - ロガー名 - レベル - メッセージ
        - 文字エンコーディング：UTF-8（日本語対応）
        """
        self.logger = logging.getLogger("api_logger")
        
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def log_request(self, endpoint: str, method: str, user_id: str = None, request_body: Dict[str, Any] = None):
        """
        APIリクエストをログに記録する
        
        クライアントからのAPIリクエストの詳細情報を構造化されたJSON形式で記録します。
        セキュリティ上の理由から、パスワードなどの機密情報は除外してログに記録してください。
        
        Args:
            endpoint (str): リクエストされたエンドポイント（例："/auth/login"）
            method (str): HTTPメソッド（GET, POST, PUT, DELETE等）
            user_id (str, optional): リクエストを送信したユーザーID（認証済みの場合）
            request_body (Dict[str, Any], optional): リクエストボディの内容（機密情報は除外）
            
        ログ出力例:
            REQUEST: {
                "type": "REQUEST",
                "timestamp": "2025-01-10T08:30:45.123456",
                "endpoint": "/auth/login",
                "method": "POST",
                "user_id": "yamada",
                "request_body": {"user_id": "yamada"}
            }
        """
        log_data = {
            "type": "REQUEST",                                    # ログの種類
            "timestamp": datetime.utcnow().isoformat(),          # UTC時刻のISO 8601形式
            "endpoint": endpoint,                                 # APIエンドポイント
            "method": method,                                     # HTTPメソッド
            "user_id": user_id,                                  # ユーザーID（認証済みの場合）
            "request_body": request_body                         # リクエストボディ（機密情報除外）
        }
        
        self.logger.info(f"REQUEST: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_response(self, endpoint: str, method: str, status_code: int, user_id: str = None, 
                    response_body: Dict[str, Any] = None, processing_time: float = None):
        """
        APIレスポンスをログに記録する
        
        サーバーからクライアントへのAPIレスポンスの詳細情報を構造化されたJSON形式で記録します。
        処理時間も記録することで、パフォーマンス分析に活用できます。
        
        Args:
            endpoint (str): レスポンスしたエンドポイント（例："/auth/login"）
            method (str): HTTPメソッド（GET, POST, PUT, DELETE等）
            status_code (int): HTTPステータスコード（200, 400, 500等）
            user_id (str, optional): レスポンス対象のユーザーID
            response_body (Dict[str, Any], optional): レスポンスボディの内容（機密情報は除外）
            processing_time (float, optional): 処理時間（秒単位）
            
        ログ出力例:
            RESPONSE: {
                "type": "RESPONSE",
                "timestamp": "2025-01-10T08:30:45.456789",
                "endpoint": "/auth/login",
                "method": "POST",
                "status_code": 200,
                "user_id": "yamada",
                "response_body": {"token_generated": true},
                "processing_time_ms": 150.5
            }
        """
        log_data = {
            "type": "RESPONSE",                                   # ログの種類
            "timestamp": datetime.utcnow().isoformat(),          # UTC時刻のISO 8601形式
            "endpoint": endpoint,                                 # APIエンドポイント
            "method": method,                                     # HTTPメソッド
            "status_code": status_code,                          # HTTPステータスコード
            "user_id": user_id,                                  # ユーザーID
            "response_body": response_body,                      # レスポンスボディ（機密情報除外）
            "processing_time_ms": processing_time * 1000 if processing_time else None  # 処理時間（ミリ秒）
        }
        
        self.logger.info(f"RESPONSE: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_error(self, endpoint: str, method: str, error: str, user_id: str = None):
        """
        APIエラーをログに記録する
        
        API処理中に発生したエラーの詳細情報を構造化されたJSON形式で記録します。
        エラーログは問題の特定とデバッグに重要な情報を提供します。
        
        Args:
            endpoint (str): エラーが発生したエンドポイント（例："/minutes/generate"）
            method (str): HTTPメソッド（GET, POST, PUT, DELETE等）
            error (str): エラーの詳細メッセージ
            user_id (str, optional): エラーが発生したユーザーID
            
        ログ出力例:
            ERROR: {
                "type": "ERROR",
                "timestamp": "2025-01-10T08:30:45.789012",
                "endpoint": "/minutes/generate",
                "method": "POST",
                "user_id": "yamada",
                "error": "OpenAI APIエラーが発生しました: Rate limit exceeded"
            }
        """
        log_data = {
            "type": "ERROR",                                     # ログの種類
            "timestamp": datetime.utcnow().isoformat(),          # UTC時刻のISO 8601形式
            "endpoint": endpoint,                                 # エラー発生エンドポイント
            "method": method,                                     # HTTPメソッド
            "user_id": user_id,                                  # ユーザーID
            "error": error                                       # エラーメッセージ
        }
        
        self.logger.error(f"ERROR: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_auth_attempt(self, user_id: str, success: bool, ip_address: str = None):
        """
        認証試行をログに記録する
        
        ユーザーのログイン試行（成功・失敗）を構造化されたJSON形式で記録します。
        セキュリティ監視と不正アクセス検知に重要な情報を提供します。
        
        Args:
            user_id (str): 認証を試行したユーザーID
            success (bool): 認証の成功/失敗（True: 成功, False: 失敗）
            ip_address (str, optional): 認証試行元のIPアドレス
            
        ログ出力例（成功時）:
            AUTH: {
                "type": "AUTH_ATTEMPT",
                "timestamp": "2025-01-10T08:30:45.345678",
                "user_id": "yamada",
                "success": true,
                "ip_address": "192.168.1.100"
            }
            
        ログ出力例（失敗時）:
            AUTH: {
                "type": "AUTH_ATTEMPT",
                "timestamp": "2025-01-10T08:30:45.345678",
                "user_id": "invalid_user",
                "success": false,
                "ip_address": "192.168.1.100"
            }
        """
        log_data = {
            "type": "AUTH_ATTEMPT",                              # ログの種類
            "timestamp": datetime.utcnow().isoformat(),          # UTC時刻のISO 8601形式
            "user_id": user_id,                                  # 認証試行ユーザーID
            "success": success,                                   # 認証成功/失敗
            "ip_address": ip_address                             # 認証試行元IPアドレス
        }
        
        level = logging.INFO if success else logging.WARNING
        
        self.logger.log(level, f"AUTH: {json.dumps(log_data, ensure_ascii=False)}")

api_logger = APILogger()
