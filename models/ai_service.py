"""
AI比較アプリケーション - AIサービス情報管理モジュール
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class AIService:
    """AIサービスの情報を保持するデータクラス"""
    name: str
    display_name: str
    url: str
    profile_name: str
    description: str = ""


class AIServiceManager:
    """AIサービス情報を管理するクラス"""
    
    def __init__(self):
        self.text_ai_services: Dict[str, AIService] = {
            'chatgpt': AIService(
                name='chatgpt',
                display_name='ChatGPT',
                url='https://chatgpt.com/',  # 新しいドメイン（自動的に日本語UIになります）
                profile_name='chatgpt_profile',
                description='OpenAI ChatGPT'
            ),
            'gemini': AIService(
                name='gemini',
                display_name='Gemini',
                url='https://gemini.google.com/app?hl=ja',
                profile_name='gemini_profile',
                description='Google Gemini'
            ),
            'claude': AIService(
                name='claude',
                display_name='Claude',
                url='https://claude.ai/new',  # 新しいチャット画面（自動で日本語UIになります）
                profile_name='claude_profile',
                description='Anthropic Claude'
            )
        }
        
        self.image_ai_services: Dict[str, AIService] = {
            'gemini_nano': AIService(
                name='gemini_nano',
                display_name='Gemini (nanoibanana)',
                url='https://gemini.google.com/app?hl=ja',
                profile_name='gemini_nano_profile',
                description='Google Gemini - 画像生成'
            ),
            'imagefx': AIService(
                name='imagefx',
                display_name='ImageFX',
                url='https://labs.google/fx/ja',
                profile_name='imagefx_profile',
                description='Google ImageFX'
            ),
            'deepl': AIService(
                name='deepl',
                display_name='DeepL',
                url='https://www.deepl.com/ja/translator#ja/en/',
                profile_name='deepl_profile',
                description='DeepL翻訳'
            )
        }
    
    def get_text_ai_service(self, name: str) -> AIService:
        """文章AIサービスを取得する"""
        return self.text_ai_services.get(name)
    
    def get_image_ai_service(self, name: str) -> AIService:
        """画像AIサービスを取得する"""
        return self.image_ai_services.get(name)
    
    def get_all_text_ai_services(self) -> list[AIService]:
        """全ての文章AIサービスを取得する"""
        return list(self.text_ai_services.values())
    
    def get_all_image_ai_services(self) -> list[AIService]:
        """全ての画像AIサービスを取得する"""
        return list(self.image_ai_services.values())
