
from datetime import datetime, timedelta  # 日時操作（トークン有効期限設定用）
from typing import Optional  # 型ヒント（None値を許可する型）
from jose import JWTError, jwt  # JWT（JSON Web Token）の生成・検証ライブラリ
from passlib.context import CryptContext  # パスワードハッシュ化ライブラリ（bcrypt使用）
from sqlalchemy.orm import Session  # データベースセッション型
from models.user import User  # ユーザーデータベースモデル
from schemas.user import UserCreate  # ユーザー作成用Pydanticスキーマ
import os  # 環境変数取得用
from dotenv import load_dotenv  # .envファイルから環境変数読み込み

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    """
    認証管理クラス
    JWT認証システムの中核となるクラスで、以下の機能を提供します：
    
    - パスワードのハッシュ化と検証
    - JWTトークンの生成と検証
    - ユーザー認証処理
    - ユーザー作成・取得処理
    
    すべてのメソッドはstaticmethodとして実装されており、
    インスタンス化せずに直接呼び出すことができます。
    """
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        平文パスワードとハッシュ化パスワードを照合する
        
        ログイン時にユーザーが入力したパスワードが正しいかを確認するために使用されます。
        bcryptアルゴリズムを使用して安全に照合を行います。
        
        引数:
            plain_password (str): ユーザーが入力した平文パスワード
            hashed_password (str): データベースに保存されているハッシュ化パスワード
            
        戻り値:
            bool: パスワードが一致する場合True、一致しない場合False
            
        使用例:
            is_valid = AuthManager.verify_password("user_input", stored_hash)
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        平文パスワードをハッシュ化する
        
        ユーザー登録時やパスワード変更時に、平文パスワードを安全なハッシュ値に変換します。
        bcryptアルゴリズムを使用し、ソルト付きでハッシュ化を行います。
        
        引数:
            password (str): ハッシュ化する平文パスワード
            
        戻り値:
            str: bcryptでハッシュ化されたパスワード文字列
            
        使用例:
            hashed = AuthManager.get_password_hash("user_password")
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """
        JWTアクセストークンを生成する
        
        ユーザー認証成功時に、保護されたエンドポイントへのアクセスに使用する
        JWTトークンを生成します。トークンにはユーザーIDと有効期限が含まれます。
        
        引数:
            data (dict): トークンに含めるデータ（通常は{"sub": user_id}）
            expires_delta (Optional[timedelta]): カスタム有効期限（指定しない場合はデフォルト値を使用）
            
        戻り値:
            str: 署名付きJWTトークン文字列
            
        使用例:
            token = AuthManager.create_access_token({"sub": "user123"})
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        JWTトークンを検証してユーザーIDを取得する
        
        保護されたエンドポイントへのアクセス時に、クライアントから送信された
        JWTトークンが有効かを確認し、含まれているユーザーIDを取得します。
        
        引数:
            token (str): 検証するJWTトークン文字列
            
        戻り値:
            Optional[str]: トークンが有効な場合はユーザーID、無効な場合はNone
            
        使用例:
            user_id = AuthManager.verify_token("eyJhbGciOiJIUzI1NiIs...")
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            user_id: str = payload.get("sub")
            
            if user_id is None:
                return None
                
            return user_id
            
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, user_id: str, password: str) -> Optional[User]:
        """
        ユーザー認証を行う
        
        ログイン時にユーザーIDとパスワードの組み合わせが正しいかを確認します。
        データベースからユーザーを取得し、パスワードを照合します。
        
        引数:
            db (Session): データベースセッション
            user_id (str): 認証するユーザーID
            password (str): 認証する平文パスワード
            
        戻り値:
            Optional[User]: 認証成功時はUserオブジェクト、失敗時はNone
            
        使用例:
            user = AuthManager.authenticate_user(db, "yamada", "password123")
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            return None
            
        if not AuthManager.verify_password(password, user.password_hash):
            return None
            
        return user
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        新規ユーザーを作成する
        
        ユーザー登録時に新しいユーザーアカウントをデータベースに作成します。
        パスワードは自動的にハッシュ化されて保存されます。
        
        引数:
            db (Session): データベースセッション
            user (UserCreate): ユーザー作成情報（user_id, password）
            
        戻り値:
            User: 作成されたユーザーオブジェクト（データベースから取得した最新情報）
            
        例外:
            IntegrityError: ユーザーIDが既に存在する場合（一意制約違反）
            
        使用例:
            new_user = AuthManager.create_user(db, UserCreate(user_id="yamada", password="pass123"))
        """
        hashed_password = AuthManager.get_password_hash(user.password)
        
        db_user = User(
            user_id=user.user_id,
            password_hash=hashed_password
        )
        
        db.add(db_user)
        
        db.commit()
        
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def get_user_by_user_id(db: Session, user_id: str) -> Optional[User]:
        """
        ユーザーIDでユーザーを取得する
        
        指定されたユーザーIDに対応するユーザー情報をデータベースから取得します。
        ユーザー存在確認やプロフィール取得などで使用されます。
        
        引数:
            db (Session): データベースセッション
            user_id (str): 取得するユーザーのID
            
        戻り値:
            Optional[User]: ユーザーが存在する場合はUserオブジェクト、存在しない場合はNone
            
        使用例:
            user = AuthManager.get_user_by_user_id(db, "yamada")
        """
        return db.query(User).filter(User.user_id == user_id).first()
