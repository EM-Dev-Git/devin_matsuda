from fastapi import APIRouter, HTTPException
from typing import List
from schema.lim import (
    PromptModel, QuestionRequest, QuestionResponse, 
    PromptCreateRequest, PromptUpdateRequest, ErrorResponse
)
from module.prompt import prompt_manager
from module.lim import azure_openai_client

router = APIRouter()


@router.get("/prompts", response_model=List[PromptModel])
async def get_prompts():
    """全てのプロンプトを取得"""
    return prompt_manager.get_all_prompts()


@router.post("/prompts", response_model=PromptModel)
async def create_prompt(prompt_request: PromptCreateRequest):
    """新しいプロンプトを作成"""
    prompt = PromptModel(
        id=prompt_request.id,
        name=prompt_request.name,
        content=prompt_request.content,
        description=prompt_request.description
    )
    return prompt_manager.create_prompt(prompt)


@router.get("/prompts/{prompt_id}", response_model=PromptModel)
async def get_prompt(prompt_id: str):
    """特定のプロンプトを取得"""
    prompt = prompt_manager.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.put("/prompts/{prompt_id}", response_model=PromptModel)
async def update_prompt(prompt_id: str, prompt_request: PromptUpdateRequest):
    """プロンプトを更新"""
    prompt = prompt_manager.update_prompt(
        prompt_id=prompt_id,
        name=prompt_request.name,
        content=prompt_request.content,
        description=prompt_request.description
    )
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """プロンプトを削除"""
    success = prompt_manager.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"message": "Prompt deleted successfully"}


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(question_request: QuestionRequest):
    """質問を送信してAI回答を取得"""
    prompt_content = None
    prompt_used = None
    
    if question_request.prompt_id:
        prompt = prompt_manager.get_prompt(question_request.prompt_id)
        if prompt:
            prompt_content = prompt.content
            prompt_used = prompt.name
        else:
            raise HTTPException(status_code=404, detail="Prompt not found")
    
    try:
        answer = await azure_openai_client.generate_response(
            question=question_request.question,
            prompt_content=prompt_content
        )
        
        return QuestionResponse(
            question=question_request.question,
            answer=answer,
            prompt_used=prompt_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
