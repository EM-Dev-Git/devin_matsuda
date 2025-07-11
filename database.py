
from sqlalchemy import create_engine  # データベースエンジンを作成するためのクラス
from sqlalchemy.ext.declarative import declarative_base  # ORMモデルのベースクラスを作成
from sqlalchemy.orm import sessionmaker  # データベースセッションを作成するためのクラス
from dotenv import load_dotenv  # .envファイルから環境変数を読み込む
import os  # 環境変数を取得するためのライブラリ

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    データベースセッションを取得する依存性注入関数
    FastAPIのDependsで使用され、各エンドポイントでデータベースアクセスを提供します
    
    使用例:
    @app.get("/users/")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    
    戻り値:
        Session: データベースセッションオブジェクト
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    データベーステーブルを作成する関数
    アプリケーション起動時に呼び出され、定義されたすべてのモデルに対応するテーブルを作成します
    
    既にテーブルが存在する場合は何も行わず、新しいテーブルのみが作成されます
    マイグレーション機能は含まれていないため、スキーマ変更時は手動対応が必要です
    """
    Base.metadata.create_all(bind=engine)
