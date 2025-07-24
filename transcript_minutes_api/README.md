# Transcript Minutes API

Microsoft Graph SDKを使用してトランスクリプトを取得し、OpenAI GPTで議事録を自動生成するFastAPI アプリケーション。

## 機能

- JWT認証によるセキュアなユーザー認証
- Microsoft Graph SDK統合によるTeamsトランスクリプト取得
- OpenAI GPTを使用した高品質な議事録生成
- ユーザー情報のデータベース管理
- 包括的なログ機能

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`を`.env`にコピーして、必要な値を設定してください。

```bash
cp .env.example .env
```

### 3. Microsoft Graph アプリケーションの設定

Azure Active Directoryでアプリケーションを登録し、以下の権限を付与してください：

- `OnlineMeetingTranscript.Read.All` (Application permission)

### 4. アプリケーションの起動

```bash
uvicorn main:app --reload
```

## API エンドポイント

### 認証

- `POST /auth/register` - 新規ユーザー登録
- `POST /auth/login` - ユーザーログイン

### トランスクリプト処理

- `POST /transcript/generate` - 直接入力されたトランスクリプトから議事録生成
- `GET /transcript/meetings` - Microsoft Graphからミーティング一覧取得
- `GET /transcript/meetings/{meeting_id}/transcripts` - 特定ミーティングのトランスクリプト一覧取得
- `POST /transcript/generate-from-graph` - Graph APIから取得したトランスクリプトで議事録生成
- `GET /transcript/history` - 議事録履歴取得

## 使用方法

1. ユーザー登録またはログインしてJWTトークンを取得
2. Authorizationヘッダーにトークンを設定
3. Microsoft Graph統合機能またはマニュアル入力で議事録を生成

## 技術スタック

- **フレームワーク**: FastAPI
- **認証**: JWT (JSON Web Token)
- **データベース**: SQLite + SQLAlchemy
- **AI**: OpenAI GPT API
- **Microsoft Graph**: msgraph-sdk + azure-identity
- **ログ**: Python logging
