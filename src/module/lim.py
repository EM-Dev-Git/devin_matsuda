from openai import AzureOpenAI
from typing import Optional
from config import settings


class AzureOpenAIClient:
    def __init__(self):
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        
        if settings.azure_openai_configured:
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version="2024-02-01",
                    azure_endpoint=self.endpoint
                )
                self.credentials_available = True
            except Exception as e:
                self.client = None
                self.credentials_available = False
                print(f"Azure OpenAI client initialization failed: {e}")
                print("Running in demo mode.")
        else:
            self.client = None
            self.credentials_available = False
            print("Azure OpenAI credentials not found. Running in demo mode.")
    
    async def generate_response(self, question: str, prompt_content: Optional[str] = None) -> str:
        if not self.credentials_available:
            demo_response = f"""
【デモモード】Azure OpenAI APIの認証情報が設定されていないため、デモ応答を返しています。

質問: {question}

使用されたプロンプト: {prompt_content[:100] + '...' if prompt_content and len(prompt_content) > 100 else prompt_content or 'なし'}

実際のAI応答を取得するには、env/.envファイルに以下の環境変数を設定してください：
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT  
- AZURE_OPENAI_DEPLOYMENT_NAME

これはシステムが正常に動作していることを示すデモ応答です。
            """.strip()
            return demo_response
        
        try:
            messages = []
            
            if prompt_content:
                messages.append({
                    "role": "system",
                    "content": prompt_content
                })
            
            messages.append({
                "role": "user", 
                "content": question
            })
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Azure OpenAI APIエラーが発生しました: {str(e)}"


azure_openai_client = AzureOpenAIClient()
