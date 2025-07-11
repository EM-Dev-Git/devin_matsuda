
from sqlalchemy import Column, Integer, String, DateTime  # SQLAlchemyのカラム型定義
from sqlalchemy.sql import func  # SQL関数（現在時刻取得など）を使用するためのモジュール
from database import Base  # データベース設定ファイルからベースクラスをインポート

class User(Base):
    """
    ユーザー情報を管理するデータベースモデル
    JWT認証システムで使用されるユーザーアカウント情報を格納します
    
    このモデルは以下の機能を提供します：
    - ユーザーIDとパスワードハッシュの管理
    - アカウント作成・更新日時の自動記録
    - ユーザーIDの一意性制約
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    
    password_hash = Column(String(255), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
