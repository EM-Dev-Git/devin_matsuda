# AI質問応答システム

Azure OpenAIを使用したFastAPIベースの質問応答システムです。Pythonでプロンプトを管理し、ブラウザから質問を送信してAIからの回答を取得できます。

## 機能

- 📝 **プロンプト管理**: Pythonでプロンプトを作成・編集・管理
- 💬 **質問応答**: ブラウザから質問を送信してAIからの回答を取得
- 🤖 **Azure OpenAI統合**: Azure OpenAI APIを使用した高品質な回答生成
- 🌐 **Webインターフェース**: 直感的なブラウザベースのUI
- ⚡ **FastAPI**: 高速で現代的なPython Webフレームワーク

## 必要な環境

- Python 3.8以上
- Azure OpenAIアカウントとAPIキー
- WSL環境（推奨）

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、Azure OpenAIの設定を入力してください：

```bash
cp .env.example .env
```

`.env`ファイルを編集して以下の値を設定：

```env
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
```

### 3. アプリケーションの起動

```bash
python main.py
```

または

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 使用方法

1. ブラウザで `http://localhost:8000` にアクセス
2. **プロンプト管理**セクションでプロンプトを作成・管理
3. **質問応答**セクションで質問を入力し、使用するプロンプトを選択
4. 「質問する」ボタンをクリックしてAIからの回答を取得

## API エンドポイント

### プロンプト管理

- `GET /prompts` - 全てのプロンプトを取得
- `POST /prompts` - プロンプトを作成または更新
- `GET /prompts/{prompt_id}` - 特定のプロンプトを取得
- `DELETE /prompts/{prompt_id}` - プロンプトを削除

### 質問応答

- `POST /ask` - 質問を送信して回答を取得

### その他

- `GET /` - メインのWebインターフェース

## プロジェクト構造

```
/
├── main.py                 # FastAPIアプリケーションのエントリーポイント
├── azure_openai_client.py  # Azure OpenAI統合
├── prompt_manager.py       # プロンプト管理システム
├── models.py              # Pydanticモデル（API用）
├── templates/             # HTMLテンプレート
│   └── index.html         # メインのWebインターフェース
├── static/               # CSS/JSファイル（将来の拡張用）
├── requirements.txt      # Python依存関係
├── .env.example         # 環境変数テンプレート
└── README.md           # このファイル
```

## 技術スタック

- **FastAPI**: 高速なPython Webフレームワーク
- **Azure OpenAI**: AI回答生成
- **Jinja2**: HTMLテンプレートエンジン
- **Pydantic**: データバリデーション
- **Uvicorn**: ASGIサーバー

## 開発

### 開発モードでの起動

```bash
uvicorn main:app --reload
```

### 新しいプロンプトの追加

プロンプトはWebインターフェースから追加できますが、プログラムで追加する場合は`prompt_manager.py`の`_initialize_default_prompts`メソッドを編集してください。

## 注意事項

- Azure OpenAIのAPIキーは`.env`ファイルに保存し、リポジトリにコミットしないでください
- 本番環境では適切なセキュリティ設定を行ってください
- プロンプトは現在メモリ内に保存されます（アプリケーション再起動時にリセット）

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
