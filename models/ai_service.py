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
    user_agent: str = None  # Noneの場合はデフォルトUAを使用



class AIServiceManager:
    """AIサービス情報を管理するクラス"""
    
    def __init__(self):
        self.text_ai_services: Dict[str, AIService] = {
            'chatgpt': AIService(
                name='chatgpt',
                display_name='ChatGPT',
                url='https://chatgpt.com/',  # 新しいドメイン（自動的に日本語UIになります）
                profile_name='chatgpt_profile',
                description='質問応答や画像生成(色味にクセあり)'
            ),
            'gemini': AIService(
                name='gemini',
                display_name='Gemini',
                url='https://gemini.google.com/app?hl=ja',
                profile_name='gemini_profile',
                description='質問応答、画像生成は条件に「～の画風で」をつけると、その画風で生成'
            )
        }
        
        self.image_ai_services: Dict[str, AIService] = {
            'imagefx': AIService(
                name='imagefx',
                display_name='ImageFX',
                url='https://labs.google/fx/ja',
                profile_name='imagefx_profile',
                description='試験的AIツール Whisk(画/動の複合),Flow(動画),ImageFX(画像),MusicFX(音楽)'
            ),
            'deepl': AIService(
                name='deepl',
                display_name='DeepL',
                url='https://www.deepl.com/ja/translator#ja/en/',
                profile_name='deepl_profile',
                description='命令文JP➔EN翻訳'
            )
        }
        
        # adobe用
        self.gemini_image_services: Dict[str, AIService] = {
            'adobeexpress': AIService(
                name='adobeexpress',
                display_name='Adobe Express',
                url='https://new.express.adobe.com/',
                profile_name='adobeexpress_profile',
                description='画像編集、動画編集、デザインテンプレート'
            )
        }
        
        # NotebookLM専用タブ
        self.audio_ai_services: Dict[str, AIService] = {
            'notebooklm': AIService(
                name='notebooklm',
                display_name='NotebookLM',
                url='https://notebooklm.google.com/',
                profile_name='notebooklm_profile',
                description='動画音声の要約、登録資料の要約や辞書化など'
            )
        }
        
        # 動画生成AIタブ
        self.video_ai_services: Dict[str, AIService] = {
            'sora': AIService(
                name='sora',
                display_name='OpenAI Sora',
                url='https://sora.chatgpt.com/',
                profile_name='sora_profile',
                description='動画生成AI (OpenAI)',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
        }
        
        # 開発者向けタブ
        self.developer_ai_services: Dict[str, AIService] = {
            'googleaistudio': AIService(
                name='googleaistudio',
                display_name='Google AI Studio',
                url='https://aistudio.google.com/',
                profile_name='googleaistudio_profile',
                description='Geminiモデルのプロトタイピングと実験（開発者向け）'
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
    
    def get_all_gemini_image_services(self) -> list[AIService]:
        """全てのGemini画像生成サービスを取得する"""
        return list(self.gemini_image_services.values())
    
    def get_audio_ai_service(self, name: str) -> AIService:
        """音声AIサービスを取得する"""
        return self.audio_ai_services.get(name)
    
    def get_all_audio_ai_services(self) -> list[AIService]:
        """全ての音声AIサービスを取得する"""
        return list(self.audio_ai_services.values())
    
    def get_all_video_ai_services(self) -> list[AIService]:
        """全ての動画AIサービスを取得する"""
        return list(self.video_ai_services.values())
    
    def get_all_developer_ai_services(self) -> list[AIService]:
        """全ての開発者向けAIサービスを取得する"""
        return list(self.developer_ai_services.values())
