"""
AI比較アプリケーション - AI比較ウィジェットモジュール
3つのAIサービスを横並びで表示するウィジェット
"""

from PySide6.QtCore import Qt, Signal, QStandardPaths
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEngineDownloadRequest
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QLabel
import os
import mimetypes
import re

from .web_view import LazyWebView
from models.ai_service import AIService
from utils.settings import Settings


class AIComparisonWidget(QWidget):
    """AI比較ウィジェット - 3つのWebViewを横並びで表示"""
    
    tab_activated = Signal()  # タブがアクティブになったシグナル
    
    def __init__(self, services: list[AIService], settings: Settings, parent=None, custom_sizes=None):
        super().__init__(parent)
        
        self.services = services
        self.settings = settings
        self.lazy_views: list[LazyWebView] = []
        self.is_initialized = False
        self.custom_sizes = custom_sizes  # カスタムスプリッターサイズ
        
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
            
            # User-Agentの設定（指定がある場合）
            if service.user_agent:
                profile.setHttpUserAgent(service.user_agent)
            
            # WebEngineSettingsの設定（Googleログイン対策）
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
            
            # Adobe Expressエディタ画面対策：WebGL/Canvas高速化
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
            
            # ダウンロードハンドラの設定
            profile.downloadRequested.connect(self._handle_download)
            
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
            
            # 説明文ラベル
            description_label = QLabel(service.description)
            description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            description_label.setStyleSheet("""
                QLabel {
                    background-color: #2D2D2D;
                    color: #5B9BD5;
                    padding: 3px;
                    font-size: 13.5px;
                    border-bottom: 1px solid #404040;
                }
            """)
            
            # ストレッチファクターでWebViewを大きく表示
            container_layout.addWidget(title_label, 0)  # ストレッチなし（固定サイズ）
            container_layout.addWidget(description_label, 0)  # ストレッチなし（固定サイズ）
            container_layout.addWidget(lazy_view, 1)    # ストレッチあり（残りスペース全体）
            
            # スプリッターに追加
            self.splitter.addWidget(container)
            self.lazy_views.append(lazy_view)
        
        # スプリッターのサイズ設定
        if self.custom_sizes:
            # カスタムサイズが指定されている場合
            total = sum(self.custom_sizes)
            base_width = 1200
            sizes = [int(base_width * size / total) for size in self.custom_sizes]
            self.splitter.setSizes(sizes)
        else:
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
        # 自動サスペンドが有効な場合のみ、ビューをサスペンド
        # デフォルトはFalse（タブ切り替え時にビュー状態を維持）
        if self.settings.get('auto_suspend', False):
            for i, lazy_view in enumerate(self.lazy_views):
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
    
    def _handle_download(self, download):
        """ダウンロードリクエストのハンドリング"""
        # ユーザーのダウンロードフォルダを取得
        downloads_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation
        )
        
        # ファイル名の取得
        file_name = download.downloadFileName()
        
        # Windowsで無効な文字を置換（: / \ ? * " < > |）
        file_name = re.sub(r'[\\/:*?"<>|]', '_', file_name)
        
        # 拡張子がない場合の補完処理
        base_name, ext = os.path.splitext(file_name)
        if not ext:
            mime_type = download.mimeType()
            if mime_type:
                # 一般的な画像形式のフォールバック
                if mime_type == "image/png":
                    ext = ".png"
                elif mime_type == "image/jpeg":
                    ext = ".jpg"
                elif mime_type == "image/webp":
                    ext = ".webp"
                else:
                    # その他の形式はmimetypesで推測
                    guessed = mimetypes.guess_extension(mime_type)
                    if guessed:
                        ext = guessed
            
            # それでも拡張子がない場合、デフォルトでpngを試す（Geminiの画像生成用）
            if not ext and "image" in str(mime_type):
                 ext = ".png"
                 
            if ext:
                file_name = f"{base_name}{ext}"
        
        file_path = os.path.join(downloads_path, file_name)
        
        # 同名ファイルが存在する場合は番号を付ける
        counter = 1
        base_name, ext = os.path.splitext(file_name)
        while os.path.exists(file_path):
            file_name = f"{base_name} ({counter}){ext}"
            file_path = os.path.join(downloads_path, file_name)
            counter += 1
        
        # ダウンロードパスを設定して開始
        download.setDownloadDirectory(downloads_path)
        download.setDownloadFileName(file_name)
        download.accept()
        
        # ダウンロード状態の監視
        download.stateChanged.connect(
            lambda state: self._on_download_state_changed(state, download)
        )
        
        print(f"ダウンロード開始: {file_name} -> {file_path}")
    
    def _on_download_state_changed(self, state, download):
        """ダウンロード状態変更時の処理"""
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            print(f"ダウンロード完了: {download.downloadFileName()}")
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            print(f"ダウンロードキャンセル: {download.downloadFileName()}")
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            print(f"ダウンロード中断: {download.downloadFileName()}")
    
    def get_memory_info(self) -> dict:
        """メモリ情報を取得"""
        info = {
            'total_views': len(self.lazy_views),
            'loaded_views': sum(1 for v in self.lazy_views if v.is_view_loaded()),
            'suspended_views': sum(1 for v in self.lazy_views 
                                  if v.is_view_loaded() and v.web_view.is_suspended)
        }
        return info
