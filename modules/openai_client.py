
from openai import OpenAI  # OpenAI公式ライブラリ（GPTモデルとの通信用）
from typing import Optional  # 型ヒント（None値を許可する型）
import os  # 環境変数取得用
from dotenv import load_dotenv  # .envファイルから環境変数読み込み
import logging  # ログ出力用

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIClient:
    """
    OpenAI APIクライアントクラス
    OpenAI GPTモデルとの通信を管理し、Teams会議トランスクリプトから議事録を生成します
    
    主な機能：
    - OpenAI API認証情報の管理
    - GPTモデルを使用したテキスト生成
    - デモモード（API認証情報がない場合の代替機能）
    - エラーハンドリングとログ記録
    
    使用例：
        client = OpenAIClient()
        minutes = await client.generate_completion(system_prompt, transcript)
    """
    
    def __init__(self):
        """
        OpenAIクライアントの初期化
        
        環境変数からAPI認証情報を取得し、OpenAIクライアントを初期化します。
        認証情報が利用できない場合は、デモモードで動作します。
        
        環境変数：
        - OPENAI_API_KEY: OpenAI APIキー（必須）
        - OPENAI_MODEL: 使用するGPTモデル名（デフォルト: gpt-3.5-turbo）
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.credentials_available = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.client = None
                self.credentials_available = False
                logger.error(f"OpenAI client initialization failed: {e}")
                print("Running in demo mode - OpenAI credentials not available.")
        else:
            self.client = None
            self.credentials_available = False
            logger.info("OpenAI API key not configured. Running in demo mode.")
            print("OpenAI API key not found. Running in demo mode.")
    
    async def generate_completion(self, system_prompt: str, user_message: str) -> str:
        """
        OpenAI GPTモデルを使用してテキスト生成を行う
        
        システムプロンプトとユーザーメッセージを組み合わせて、
        GPTモデルに議事録生成を依頼します。API認証情報が利用できない場合は
        デモレスポンスを返します。
        
        引数:
            system_prompt (str): システムプロンプト（AIの役割と指示を定義）
            user_message (str): ユーザーメッセージ（Teams会議のトランスクリプト）
            
        戻り値:
            str: 生成された議事録テキスト（Markdown形式）
            
        例外:
            Exception: OpenAI API呼び出し時のエラー（ネットワーク、認証、レート制限など）
            
        使用例:
            minutes = await client.generate_completion(
                "あなたは議事録作成の専門家です...",
                "山田: おはようございます..."
            )
        """
        if not self.credentials_available:
            return self._generate_demo_response(user_message)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},  # システムプロンプト（AIの役割定義）
                {"role": "user", "content": user_message}      # ユーザーメッセージ（トランスクリプト）
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,           # 使用するGPTモデル（gpt-3.5-turbo等）
                messages=messages,          # 会話メッセージ
                max_tokens=2000,           # 生成する最大トークン数（約1500-2000文字相当）
                temperature=0.3            # 生成の創造性レベル（0.0-1.0、低いほど一貫性重視）
            )
            
            content = response.choices[0].message.content
            logger.info("OpenAI completion generated successfully")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            error_msg = f"OpenAI APIエラーが発生しました: {str(e)}\n\nエラーが発生しました。システム管理者に連絡してください。"
            return error_msg
    
    def _generate_demo_response(self, transcript: str) -> str:
        """
        デモモード用の議事録生成機能
        
        OpenAI API認証情報が利用できない場合に、トランスクリプトを簡易分析して
        デモ用の議事録を生成します。実際のAI分析は行わず、基本的なテキスト解析のみを実行します。
        
        分析内容：
        - 発言者名の抽出（コロン区切りの形式から）
        - キーワードベースのトピック検出
        - 基本的な統計情報（文字数、参加者数など）
        
        引数:
            transcript (str): Teams会議のトランスクリプト
            
        戻り値:
            str: デモ用議事録（Markdown形式）
            
        注意:
            この機能は開発・テスト用途のみで、実際の議事録生成には適していません。
            本格運用時は必ずOpenAI API認証情報を設定してください。
        """
        lines = transcript.split('\n')
        participants = set()  # 参加者名を格納するセット（重複除去）
        topics = []          # 検出されたトピックを格納するリスト
        
        for line in lines:
            line = line.strip()
            if ':' in line and len(line.split(':')[0]) < 50:
                speaker = line.split(':')[0].strip()
                if speaker and len(speaker) < 30:
                    participants.add(speaker)
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['プロジェクト', 'タスク', '課題', '問題', '提案', '決定', '承認']):
                if len(line) > 20 and len(line) < 200:
                    topics.append(line.strip())
        
        participant_list = list(participants)[:5]
        
        demo_minutes = f"""## 会議概要
【デモモード - 実際のトランスクリプト分析】

参加者: {', '.join(participant_list) if participant_list else '不明'}
トランスクリプト文字数: {len(transcript)}文字

主要な議論内容が含まれた会議のようです。実際のOpenAI APIを使用することで、より詳細で正確な議事録を生成できます。

• 参加者数: {len(participant_list)}名
• トランスクリプト総文字数: {len(transcript)}文字
• 検出されたトピック数: {len(topics)}件
• 実際のAI分析により、より詳細な議論内容を抽出可能

• OpenAI API認証情報の設定
• 実際の会議トランスクリプトでの本格テスト
• 議事録生成精度の確認と調整

• デモモードでの基本動作確認完了
• トランスクリプト解析機能の実装確認
• 本格運用に向けたAPI設定が必要"""

        logger.info("Demo meeting minutes generated successfully")
        return demo_minutes

openai_client = OpenAIClient()
