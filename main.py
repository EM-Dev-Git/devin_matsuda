from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn

from models import PromptModel, QuestionRequest, QuestionResponse
from prompt_manager import PromptManager
from azure_openai_client import AzureOpenAIClient

app = FastAPI(title="AI質問応答システム", description="Azure OpenAIを使用した質問応答システム")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

prompt_manager = PromptManager()
openai_client = AzureOpenAIClient()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """メインページを表示"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/prompts", response_model=List[PromptModel])
async def get_prompts():
    """全てのプロンプトを取得"""
    return prompt_manager.get_all_prompts()


@app.post("/prompts")
async def create_or_update_prompt(prompt: PromptModel):
    """プロンプトを作成または更新"""
    success = prompt_manager.add_prompt(prompt)
    if not success:
        raise HTTPException(status_code=400, detail="プロンプトの保存に失敗しました")
    return {"message": "プロンプトが正常に保存されました", "prompt_id": prompt.id}


@app.get("/prompts/{prompt_id}", response_model=PromptModel)
async def get_prompt(prompt_id: str):
    """特定のプロンプトを取得"""
    prompt = prompt_manager.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="プロンプトが見つかりません")
    return prompt


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(question_request: QuestionRequest):
    """質問に対する回答を生成"""
    try:
        prompt_content = None
        prompt_used = None
        
        if question_request.prompt_id:
            prompt = prompt_manager.get_prompt(question_request.prompt_id)
            if prompt:
                prompt_content = prompt.content
                prompt_used = prompt.name
            else:
                raise HTTPException(status_code=404, detail="指定されたプロンプトが見つかりません")
        
        answer = await openai_client.generate_response(
            question_request.question, 
            prompt_content
        )
        
        return QuestionResponse(
            question=question_request.question,
            answer=answer,
            prompt_used=prompt_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回答の生成に失敗しました: {str(e)}")


@app.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """プロンプトを削除"""
    success = prompt_manager.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=400, detail="プロンプトの削除に失敗しました（デフォルトプロンプトは削除できません）")
    return {"message": "プロンプトが正常に削除されました"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
