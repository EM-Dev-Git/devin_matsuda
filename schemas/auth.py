
from pydantic import BaseModel  # Pydanticのベースモデルクラス（データ検証・シリアライゼーション用）

class LoginRequest(BaseModel):
    """
    ログインリクエストのスキーマ
    ユーザーがログインする際にクライアントから送信されるデータの形式を定義します
    
    使用例:
    POST /auth/login
    {
        "user_id": "yamada_taro",
        "password": "secure_password123"
    }
    
    このスキーマにより、以下の検証が自動的に行われます：
    - user_idとpasswordが文字列型であること
    - 両フィールドが必須であること（None値不可）
    - リクエストボディのJSON形式が正しいこと
    """
    user_id: str
    
    password: str

class LoginResponse(BaseModel):
    """
    ログインレスポンスのスキーマ
    ログイン成功時にクライアントに返されるJWTトークン情報の形式を定義します
    
    使用例:
    POST /auth/login のレスポンス（成功時）
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    
    クライアントは受信したaccess_tokenを以下の形式でAuthorizationヘッダーに設定します：
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    access_token: str
    
    token_type: str = "bearer"

class RegisterRequest(BaseModel):
    """
    ユーザー登録リクエストのスキーマ
    新規ユーザーがアカウントを作成する際にクライアントから送信されるデータの形式を定義します
    
    使用例:
    POST /auth/register
    {
        "user_id": "yamada_taro",
        "password": "secure_password123"
    }
    
    このスキーマにより、以下の検証が自動的に行われます：
    - user_idとpasswordが文字列型であること
    - 両フィールドが必須であること（None値不可）
    - リクエストボディのJSON形式が正しいこと
    
    注意: user_idの一意性チェックはビジネスロジック層で実行されます
    """
    user_id: str
    
    password: str

class RegisterResponse(BaseModel):
    """
    ユーザー登録レスポンスのスキーマ
    ユーザー登録成功時にクライアントに返される確認情報の形式を定義します
    
    使用例:
    POST /auth/register のレスポンス（成功時）
    {
        "message": "ユーザー登録が完了しました",
        "user_id": "yamada_taro"
    }
    
    登録成功後、クライアントは通常ログインAPIを呼び出してJWTトークンを取得します
    """
    message: str
    
    user_id: str
