from typing import Dict, List, Optional
from schema.lim import PromptModel


class PromptManager:
    def __init__(self):
        self.prompts: Dict[str, PromptModel] = {}
        self._initialize_default_prompts()
    
    def _initialize_default_prompts(self):
        default_prompt = PromptModel(
            id="default",
            name="デフォルトプロンプト",
            content="あなたは質問に対して丁寧で詳細な回答を提供するアシスタントです。質問に対して正確で分かりやすい回答を提供してください。",
            description="基本的な質問応答用のデフォルトプロンプト"
        )
        self.prompts[default_prompt.id] = default_prompt
    
    def get_all_prompts(self) -> List[PromptModel]:
        return list(self.prompts.values())
    
    def get_prompt(self, prompt_id: str) -> Optional[PromptModel]:
        return self.prompts.get(prompt_id)
    
    def create_prompt(self, prompt: PromptModel) -> PromptModel:
        self.prompts[prompt.id] = prompt
        return prompt
    
    def update_prompt(self, prompt_id: str, name: Optional[str] = None, 
                     content: Optional[str] = None, description: Optional[str] = None) -> Optional[PromptModel]:
        if prompt_id not in self.prompts:
            return None
        
        prompt = self.prompts[prompt_id]
        if name is not None:
            prompt.name = name
        if content is not None:
            prompt.content = content
        if description is not None:
            prompt.description = description
        
        return prompt
    
    def delete_prompt(self, prompt_id: str) -> bool:
        if prompt_id in self.prompts:
            del self.prompts[prompt_id]
            return True
        return False


prompt_manager = PromptManager()
