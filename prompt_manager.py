from typing import Dict, List, Optional
from models import PromptModel


class PromptManager:
    def __init__(self):
        self.prompts: Dict[str, PromptModel] = {}
        self._initialize_default_prompts()
    
    def _initialize_default_prompts(self):
        default_prompt = PromptModel(
            id="default",
            name="デフォルトプロンプト",
            content="あなたは親切で知識豊富なアシスタントです。質問に対して正確で分かりやすい回答を提供してください。",
            description="基本的な質問応答用のデフォルトプロンプト"
        )
        self.prompts[default_prompt.id] = default_prompt
    
    def add_prompt(self, prompt: PromptModel) -> bool:
        try:
            self.prompts[prompt.id] = prompt
            return True
        except Exception:
            return False
    
    def get_prompt(self, prompt_id: str) -> Optional[PromptModel]:
        return self.prompts.get(prompt_id)
    
    def get_all_prompts(self) -> List[PromptModel]:
        return list(self.prompts.values())
    
    def update_prompt(self, prompt_id: str, prompt: PromptModel) -> bool:
        if prompt_id in self.prompts:
            self.prompts[prompt_id] = prompt
            return True
        return False
    
    def delete_prompt(self, prompt_id: str) -> bool:
        if prompt_id in self.prompts and prompt_id != "default":
            del self.prompts[prompt_id]
            return True
        return False
