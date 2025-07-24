# Transcript to Meeting Minutes API

トランスクリプトから議事録を自動生成するFastAPI アプリケーション。Microsoft Graph SDKを使用してTeams会議のトランスクリプトを直接取得することもできます。

## 概要

このAPIは、会議のトランスクリプト（文字起こし）を受け取り、OpenAI GPTを使用して構造化された議事録を自動生成します。JWT認証によるセキュアなアクセス制御と包括的なログ機能を提供します。

## 機能

- **JWT認証**: セキュアなユーザー認証システム
- **議事録生成**: OpenAI GPTを使用した高品質な議事録作成
- **Microsoft Graph SDK統合**: Teams会議トランスクリプトの直接取得
- **データベース**: ユーザー情報の安全な保存
- **ログ機能**: 包括的なアクセス・エラーログ
- **環境変数管理**: セキュアな設定管理

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、必要な値を設定してください：

```bash
cp .env.example .env
```

`.env`ファイルの設定例：

```env
# データベース
DATABASE_URL=sqlite:///./app.db

# JWT設定
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI設定
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Microsoft Graph設定
GRAPH_CLIENT_ID=your-graph-client-id-here
GRAPH_CLIENT_SECRET=your-graph-client-secret-here
GRAPH_TENANT_ID=your-tenant-id-here

# ログ設定
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### 3. Microsoft Graph SDK セットアップ

Microsoft Graph機能を使用するには、Azure Active Directoryでアプリケーションを登録する必要があります：

1. **Azure ポータル**にアクセス
2. **Azure Active Directory** > **アプリの登録** > **新規登録**
3. アプリケーション名を入力し、**登録**をクリック
4. **API のアクセス許可** > **アクセス許可の追加** > **Microsoft Graph** > **アプリケーションのアクセス許可**
5. **OnlineMeetingTranscript.Read.All** 権限を追加
6. **管理者の同意を与える**をクリック
7. **証明書とシークレット**でクライアントシークレットを作成
8. **概要**ページからアプリケーション（クライアント）IDとディレクトリ（テナント）IDを取得

### 4. データベースの初期化

アプリケーション起動時に自動的にデータベーステーブルが作成されます。

### 5. テストユーザーの作成

初回利用時は、データベースに直接ユーザーを追加する必要があります：

```python
from modules.database import SessionLocal, User
from modules.auth import get_password_hash

db = SessionLocal()
hashed_password = get_password_hash("your_password")
user = User(user_id="test_user", password_hash=hashed_password)
db.add(user)
db.commit()
db.close()
```

## 起動方法

### 開発環境

```bash
uvicorn main:app --reload
```

### 本番環境

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API仕様

### 認証エンドポイント

#### POST /auth/login

ユーザー認証を行い、JWTトークンを取得します。

**リクエスト:**
```json
{
    "user_id": "test_user",
    "password": "your_password"
}
```

**レスポンス:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 議事録生成エンドポイント

#### POST /transcript/generate

トランスクリプトから議事録を生成します。（JWT認証必須）

**ヘッダー:**
```
Authorization: Bearer <your_jwt_token>
```

**リクエスト:**
```json
{
    "transcript": "会議の文字起こしテキスト...",
    "meeting_title": "プロジェクト進捗会議",
    "participants": ["田中", "佐藤", "鈴木"]
}
```

**レスポンス:**
```json
{
    "meeting_minutes": "# 会議議事録\n\n## 会議概要\n...",
    "generated_at": "2025-07-24T10:30:00.000Z",
    "status": "success"
}
```

## エラーハンドリング

APIは標準化されたエラーレスポンス形式を使用します：

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "エラーメッセージ",
        "details": "詳細情報（オプション）"
    }
}
```

### HTTPステータスコード

- `200`: 成功
- `400`: リクエストエラー
- `401`: 認証エラー
- `403`: 認可エラー
- `500`: サーバーエラー

## ログ

アプリケーションは以下の情報をログに記録します：

- アクセスログ（認証試行、API呼び出し）
- エラーログ（認証失敗、API エラー）
- システムログ（起動・終了）

ログファイルは環境変数`LOG_FILE`で指定された場所に保存されます（デフォルト: `app.log`）。

## セキュリティ

- パスワードはbcryptでハッシュ化して保存
- JWTトークンには適切な有効期限を設定
- 環境変数による機密情報管理
- Microsoft Graph認証（クライアント資格情報フロー）
- SQLインジェクション対策
- 入力データバリデーション

## 開発

### ディレクトリ構成

```
transcript_minutes_api/
├── routers/           # APIルーティング
│   ├── __init__.py
│   ├── auth.py       # 認証関連エンドポイント
│   └── transcript.py # 議事録生成エンドポイント
├── modules/          # ビジネスロジック
│   ├── __init__.py
│   ├── auth.py       # 認証処理
│   ├── database.py   # DB接続・操作
│   ├── openai_client.py # OpenAI連携
│   ├── graph_client.py # Microsoft Graph連携
│   └── logger.py     # ログ設定
├── schemas/          # Pydanticスキーマ
│   ├── __init__.py
│   ├── user.py       # ユーザー関連スキーマ
│   └── transcript.py # トランスクリプト関連スキーマ
├── main.py           # アプリケーションエントリーポイント
├── requirements.txt  # 依存関係
├── .env.example      # 環境変数テンプレート
├── test_graph_integration.py # Graph統合テスト
└── README.md
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

問題や質問がある場合は、GitHubのIssueを作成してください。
