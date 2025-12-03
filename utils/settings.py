"""
AI比較アプリケーション - 設定管理モジュール
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class Settings:
    """アプリケーション設定を管理するクラス"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.ai_comparison_app'
        self.config_file = self.config_dir / 'settings.json'
        self.data_dir = self.config_dir / 'data'
        self.settings: Dict[str, Any] = {}
        
        # ディレクトリの作成
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # 設定の読み込み
        self.load()
    
    def load(self):
        """設定ファイルを読み込む"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"設定ファイルの読み込みに失敗: {e}")
                self.settings = self.get_default_settings()
        else:
            self.settings = self.get_default_settings()
            self.save()
    
    def save(self):
        """設定ファイルを保存する"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存に失敗: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得する"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """設定値を設定する"""
        self.settings[key] = value
        self.save()
    
    def get_default_settings(self) -> Dict[str, Any]:
        """デフォルト設定を取得する"""
        return {
            'window_geometry': None,
            'suspend_timeout': 300,  # 5分（秒）
            'memory_warning_threshold': 6144,  # 6GB（MB）
            'tab_lazy_load': True,
            'auto_suspend': True,
            'theme': 'dark',
            'text_ai_urls': {
                'chatgpt': 'https://chat.openai.com/',
                'gemini': 'https://gemini.google.com/',
                'claude': 'https://claude.ai/'
            },
            'image_ai_urls': {
                'gemini_nano': 'https://gemini.google.com/',
                'imagefx': 'https://aitestkitchen.withgoogle.com/tools/image-fx',
                'deepl': 'https://www.deepl.com/translator'
            }
        }
    
    def get_profile_dir(self, profile_name: str) -> str:
        """プロファイルディレクトリのパスを取得する"""
        profile_dir = self.data_dir / profile_name
        profile_dir.mkdir(exist_ok=True)
        return str(profile_dir)
