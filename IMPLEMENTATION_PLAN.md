# Teams会議議事録生成システム 実装計画書

## プロジェクト概要

Teams会議のトランスクリプトからAzure OpenAIを使用して議事録を自動生成するFastAPI Webアプリケーションシステム

## 使用技術・ツール

- **バックエンド**: FastAPI (Python)
- **AI**: Azure OpenAI API
- **開発環境**: WSL (Windows Subsystem for Linux)
- **エディタ**: VSCode
- **ブラウザアクセス**: localhost:8000 (FastAPI docs使用)
- **認証**: Azure OpenAI APIキー、エンドポイント、デプロイメント名

## ディレクトリ構造

```
プロジェクト/
├── env/
│   └── .env                    # 環境変数設定ファイル
└── src/
    ├── __pycache__/           # Pythonキャッシュ
    ├── module/
    │   ├── __pycache__/
    │   ├── lim.py             # 議事録生成ロジック
    │   └── prompt.py          # プロンプト定義
    ├── router/
    │   ├── __pycache__/
    │   └── lim.py             # APIルーティング
    ├── schema/
    │   ├── __pycache__/
    │   └── lim.py             # データモデル定義
    ├── config.py              # 設定管理
    └── main.py                # FastAPIアプリケーション
```

## 機能要件

### 1. API仕様

#### エンドポイント
- `POST /api/v1/generate-minutes` - 議事録生成

#### リクエスト仕様
```json
{
  "original_transcript": "会議のトランスクリプト文字列"
}
```

#### レスポンス仕様
```json
{
  "meeting_minutes": "生成された議事録テキスト",
  "generated_at": "2025-07-10T07:24:37.123456"
}
```

### 2. ログ機能
- リクエストボディとレスポンスボディのログ出力
- 処理時間の記録
- エラーハンドリングとログ

### 3. Azure OpenAI統合
- API認証情報の管理
- プロンプトエンジニアリング
- デモモード対応（認証情報未設定時）

## 実装詳細

### 1. 環境設定 (env/.env)
```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 2. 設定管理 (src/config.py)
- 環境変数の読み込み
- Azure OpenAI設定の検証
- アプリケーション設定の一元管理

### 3. データモデル (src/schema/lim.py)
- `TranscriptRequest`: リクエストモデル
- `MeetingMinutesResponse`: レスポンスモデル
- `ErrorResponse`: エラーレスポンスモデル

### 4. プロンプト定義 (src/module/prompt.py)
- 議事録生成用プロンプトの定義
- 構造化された出力形式の指定
- 日本語対応

### 5. 議事録生成ロジック (src/module/lim.py)
- Azure OpenAI APIクライアント初期化
- 議事録生成メソッド
- デモモード実装
- エラーハンドリング

### 6. APIルーティング (src/router/lim.py)
- FastAPIルーター定義
- エンドポイント実装
- リクエスト/レスポンス処理
- ログ出力

### 7. メインアプリケーション (src/main.py)
- FastAPIアプリケーション初期化
- CORS設定
- ルーター登録
- サーバー起動設定

## 開発フロー

### Phase 1: 基盤構築
1. ディレクトリ構造作成
2. 依存関係定義 (requirements.txt)
3. 環境設定ファイル作成
4. 基本設定管理実装

### Phase 2: コア機能実装
1. データモデル定義
2. プロンプト設計・実装
3. Azure OpenAI統合
4. 議事録生成ロジック実装

### Phase 3: API実装
1. FastAPIルーター実装
2. エンドポイント作成
3. リクエスト/レスポンス処理
4. エラーハンドリング

### Phase 4: 統合・テスト
1. メインアプリケーション統合
2. ローカルサーバー起動
3. FastAPI docs経由でのテスト
4. デモモード動作確認

### Phase 5: 最終検証
1. 実際のトランスクリプトでのテスト
2. Azure OpenAI API統合テスト
3. ログ機能確認
4. エラーケース検証

## テスト戦略

### 1. 単体テスト
- 各モジュールの個別機能テスト
- プロンプト生成テスト
- データモデル検証

### 2. 統合テスト
- API エンドポイントテスト
- Azure OpenAI API統合テスト
- エラーハンドリングテスト

### 3. 手動テスト
- FastAPI docs UI経由でのテスト
- 実際の会議トランスクリプトでのテスト
- デモモード動作確認

## デプロイメント

### 1. ローカル開発
```bash
cd src
python main.py
```
- アクセス: http://localhost:8000/docs

### 2. 本番環境
- Azure OpenAI認証情報設定
- 環境変数の適切な設定
- セキュリティ考慮事項

## セキュリティ考慮事項

1. **API認証情報の保護**
   - .envファイルの適切な管理
   - 認証情報のハードコーディング禁止

2. **入力検証**
   - トランスクリプト内容の検証
   - 不正なリクエストの防止

3. **ログセキュリティ**
   - 機密情報のログ出力防止
   - 適切なログレベル設定

## 成功基準

1. **機能要件**
   - トランスクリプトから議事録生成が正常動作
   - Azure OpenAI API統合が完了
   - デモモードが正常動作

2. **技術要件**
   - 指定されたディレクトリ構造で実装
   - FastAPI docs経由でのテストが可能
   - localhost:8000でのアクセスが可能

3. **品質要件**
   - エラーハンドリングが適切
   - ログ機能が正常動作
   - コードの可読性・保守性が確保

## リスク・課題

1. **Azure OpenAI API制限**
   - レート制限への対応
   - API利用料金の考慮

2. **プロンプトエンジニアリング**
   - 日本語議事録の品質確保
   - 様々なトランスクリプト形式への対応

3. **パフォーマンス**
   - 大容量トランスクリプトの処理
   - レスポンス時間の最適化

## 今後の拡張可能性

1. **機能拡張**
   - 複数言語対応
   - 議事録テンプレートのカスタマイズ
   - ファイルアップロード機能

2. **技術拡張**
   - データベース統合
   - ユーザー認証機能
   - Web UI実装

3. **運用拡張**
   - ログ分析機能
   - パフォーマンス監視
   - 自動テスト実装
