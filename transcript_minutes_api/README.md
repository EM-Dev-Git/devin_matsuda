# Transcript to Minutes API

音声トランスクリプトから議事録を自動生成するWebAPIシステム

## 機能

- JWT認証によるユーザー管理
- トランスクリプトの投稿と管理
- OpenAI APIを使用した議事録の自動生成
- 構造化ログ出力
- RESTful API設計

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`を`.env`にコピーして、必要な値を設定してください：

```bash
cp .env.example .env
```

必須の環境変数：
- `SECRET_KEY`: JWT署名用の秘密鍵
- `OPENAI_API_KEY`: OpenAI APIキー

### 3. アプリケーションの起動

```bash
uvicorn app.main:app --reload
```

または

```bash
python -m app.main
```

## API エンドポイント

### 認証
- `POST /auth/register` - ユーザー登録
- `POST /auth/login` - ログイン
- `GET /auth/me` - 現在のユーザー情報

### ユーザー管理
- `GET /users/profile` - プロフィール取得
- `PUT /users/profile` - プロフィール更新
- `DELETE /users/profile` - アカウント削除

### トランスクリプト・議事録
- `POST /transcripts` - トランスクリプト投稿・議事録生成
- `GET /transcripts` - トランスクリプト一覧
- `GET /transcripts/{id}` - 特定のトランスクリプト取得
- `PUT /transcripts/{id}` - トランスクリプト更新
- `DELETE /transcripts/{id}` - トランスクリプト削除

## API ドキュメント

アプリケーション起動後、以下のURLでSwagger UIにアクセスできます：
- http://localhost:8000/docs

## 技術スタック

- **FastAPI**: Webフレームワーク
- **SQLAlchemy**: ORM
- **SQLite**: データベース（開発環境）
- **JWT**: 認証
- **OpenAI API**: 議事録生成
- **Structlog**: 構造化ログ
- **Pydantic**: データバリデーション

## ディレクトリ構成

```
app/
├── main.py              # アプリケーションエントリーポイント
├── config.py            # 設定管理
├── database.py          # データベース設定
├── dependencies.py      # 依存性注入
├── models/              # SQLAlchemyモデル
├── schemas/             # Pydanticスキーマ
├── routers/             # APIルーター
└── modules/             # ビジネスロジック
```
