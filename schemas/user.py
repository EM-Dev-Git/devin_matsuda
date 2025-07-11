
from pydantic import BaseModel  # Pydanticのベースモデルクラス（データ検証・シリアライゼーション用）
from datetime import datetime  # 日時型の定義

class UserBase(BaseModel):
    """
    ユーザー情報の基本スキーマ
    他のユーザー関連スキーマの共通フィールドを定義します
    
    このクラスは継承用のベースクラスとして機能し、
    ユーザーIDなどの共通フィールドを一元管理します
    """
    user_id: str

class UserCreate(UserBase):
    """
    ユーザー作成（登録）時のリクエストスキーマ
    新規ユーザー登録APIのリクエストボディで使用されます
    
    UserBaseを継承してuser_idフィールドを含み、
    さらにパスワードフィールドを追加しています
    
    使用例:
    POST /auth/register
    {
        "user_id": "yamada_taro",
        "password": "secure_password123"
    }
    """
    password: str

class User(UserBase):
    """
    ユーザー情報のレスポンススキーマ
    APIからクライアントに返されるユーザー情報の形式を定義します
    
    UserBaseを継承してuser_idフィールドを含み、
    データベースから取得される追加情報（ID、作成日時など）を含みます
    
    注意: パスワードハッシュは含まれていません（セキュリティ上の理由）
    
    使用例:
    GET /users/me のレスポンス
    {
        "id": 1,
        "user_id": "yamada_taro",
        "created_at": "2025-01-10T08:30:00Z",
        "updated_at": "2025-01-10T08:30:00Z"
    }
    """
    id: int
    
    created_at: datetime
    
    updated_at: datetime
    
    class Config:
        """
        Pydanticの設定クラス
        SQLAlchemyモデルからPydanticモデルへの変換設定を定義
        """
        from_attributes = True
