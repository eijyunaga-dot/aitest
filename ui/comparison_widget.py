"""
AI比較アプリケーション - AI比較ウィジェットモジュール
3つのAIサービスを横並びで表示するウィジェット
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QLabel

from .web_view import LazyWebView
from models.ai_service import AIService
from utils.settings import Settings


class AIComparisonWidget(QWidget):
    """AI比較ウィジェット - 3つのWebViewを横並びで表示"""
    
    tab_activated = Signal()  # タブがアクティブになったシグナル
    
    def __init__(self, services: list[AIService], settings: Settings, parent=None):
        super().__init__(parent)
        
        self.services = services
        self.settings = settings
        self.lazy_views: list[LazyWebView] = []
        self.is_initialized = False
        
        # UIの初期化
        self._init_ui()
    
    def _init_ui(self):
        """UIの初期化"""
        # メインレイアウト
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # スプリッターの作成（3つのビューを横並び）
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        
        # 各AIサービス用のLazyWebViewを作成
        for service in self.services:
            # プロファイルの作成
            profile = QWebEngineProfile(service.profile_name, self)
            profile_dir = self.settings.get_profile_dir(service.profile_name)
            profile.setPersistentStoragePath(profile_dir)
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            
            # 日本語の言語設定を追加
            profile.setHttpAcceptLanguage("ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7")
            
            # LazyWebViewの作成
            lazy_view = LazyWebView(service.url, profile, self)
            
            # コンテナウィジェットの作成（タイトル付き）
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            
            # タイトルラベル
            title_label = QLabel(service.display_name)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    padding: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    border-bottom: 1px solid #404040;
                }
            """)
            
            # ストレッチファクターでWebViewを大きく表示
            container_layout.addWidget(title_label, 0)  # ストレッチなし（固定サイズ）
            container_layout.addWidget(lazy_view, 1)    # ストレッチあり（残りスペース全体）
            
            # スプリッターに追加
            self.splitter.addWidget(container)
            self.lazy_views.append(lazy_view)
        
        # 均等分割
        total_width = 1200  # デフォルト幅
        size_per_view = total_width // len(self.services)
        self.splitter.setSizes([size_per_view] * len(self.services))
        
        # スプリッターをレイアウトに追加
        main_layout.addWidget(self.splitter)
        
        # スプリッターのスタイル
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #404040;
                width: 1px;
            }
            QSplitter::handle:hover {
                background-color: #5B8DEE;
                width: 3px;
            }
        """)
    
    def initialize_views(self):
        """ビューを初期化（遅延ロード）"""
        if not self.is_initialized:
            print(f"ビューを初期化中... ({len(self.lazy_views)}個のビュー)")
            
            # このタブがアクティブになったら、全てのビューをロード
            # （タブ遅延ロードは「タブ間」の遅延であり、タブ内は全て表示）
            for i, lazy_view in enumerate(self.lazy_views):
                print(f"  ビュー {i+1}/{len(self.lazy_views)} をロード中...")
                lazy_view.load_content()
            
            self.is_initialized = True
            print("全てのビューのロードが完了しました")
    
    def on_tab_show(self):
        """タブが表示された時の処理"""
        self.initialize_views()
        self.tab_activated.emit()
        
        # サスペンド中のビューを再開
        for lazy_view in self.lazy_views:
            if lazy_view.is_view_loaded():
                lazy_view.resume()
    
    def on_tab_hide(self):
        """タブが非表示になった時の処理"""
        # 自動サスペンドが有効な場合、全てのビューをサスペンド
        if self.settings.get('auto_suspend', True):
            for lazy_view in self.lazy_views:
                if lazy_view.is_view_loaded():
                    lazy_view.suspend()
    
    def reload_all(self):
        """全てのビューを再読み込み"""
        for lazy_view in self.lazy_views:
            if lazy_view.is_view_loaded():
                web_view = lazy_view.get_web_view()
                web_view.reload()
    
    def go_back_all(self):
        """全てのビューで戻る"""
        for lazy_view in self.lazy_views:
            if lazy_view.is_view_loaded():
                web_view = lazy_view.get_web_view()
                if web_view.history().canGoBack():
                    web_view.back()
    
    def go_forward_all(self):
        """全てのビューで進む"""
        for lazy_view in self.lazy_views:
            if lazy_view.is_view_loaded():
                web_view = lazy_view.get_web_view()
                if web_view.history().canGoForward():
                    web_view.forward()
    
    def get_memory_info(self) -> dict:
        """メモリ情報を取得"""
        info = {
            'total_views': len(self.lazy_views),
            'loaded_views': sum(1 for v in self.lazy_views if v.is_view_loaded()),
            'suspended_views': sum(1 for v in self.lazy_views 
                                  if v.is_view_loaded() and v.web_view.is_suspended)
        }
        return info
