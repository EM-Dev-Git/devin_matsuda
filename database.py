
from sqlalchemy import create_engine  # データベースエンジンを作成するためのクラスをインポート
from sqlalchemy.ext.declarative import declarative_base  # ORMモデルのベースクラスを作成するためのクラスをインポート
from sqlalchemy.orm import sessionmaker  # データベースセッションを作成するためのクラスをインポート
from dotenv import load_dotenv  # .envファイルから環境変数を読み込むライブラリをインポート
import os  # 環境変数を取得するためのライブラリをインポート

load_dotenv()  # .envファイルから環境変数を読み込んでos.environに設定

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")  # 環境変数からデータベースURLを取得（デフォルト：SQLite）

engine = create_engine(  # SQLAlchemyデータベースエンジンを作成
    DATABASE_URL,  # データベース接続URL
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}  # SQLiteの場合はマルチスレッド対応設定を追加
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # データベースセッションファクトリを作成

Base = declarative_base()  # ORMモデルの基底クラスを作成

def get_db():  # データベースセッションを取得する依存性注入関数を定義
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
    db = SessionLocal()  # セッションファクトリから新しいデータベースセッションを作成
    try:  # セッション使用の例外処理を開始
        yield db  # セッションをジェネレーターとして返す（FastAPIの依存性注入で使用）
    finally:  # セッション使用完了後の処理
        db.close()  # データベースセッションを閉じてリソースを解放

def create_tables():  # データベーステーブルを作成する関数を定義
    """
    データベーステーブルを作成する関数
    アプリケーション起動時に呼び出され、定義されたすべてのモデルに対応するテーブルを作成します
    
    既にテーブルが存在する場合は何も行わず、新しいテーブルのみが作成されます
    マイグレーション機能は含まれていないため、スキーマ変更時は手動対応が必要です
    """
    Base.metadata.create_all(bind=engine)  # Baseクラスから継承されたすべてのモデルのテーブルをデータベースエンジンに作成
