"""
AI比較アプリケーション - カスタムWebビューモジュール
メモリ最適化機能を備えたWebViewコンポーネント
"""

from PySide6.QtCore import QUrl, QTimer, Signal, Qt
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout


class SuspendableWebView(QWebEngineView):
    """サスペンド機能を持つWebView"""
    
    suspended = Signal(bool)  # サスペンド状態変更シグナル
    
    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(parent)
        
        # プロファイルの設定
        page = QWebEnginePage(profile, self)
        self.setPage(page)
        
        # サスペンド管理
        self.is_suspended = False
        self.suspend_timer = QTimer(self)
        self.suspend_timer.timeout.connect(self._auto_suspend)
        self.suspend_timeout = 300000  # 5分（ミリ秒）
        
        # ページロード完了時にタイマーをリセット
        self.loadFinished.connect(self._on_load_finished)
    
    def _on_load_finished(self):
        """ページロード完了時の処理"""
        self._reset_suspend_timer()
    
    def _reset_suspend_timer(self):
        """サスペンドタイマーをリセット"""
        if hasattr(self, 'suspend_timer'):
            self.suspend_timer.stop()
            if not self.is_suspended:
                self.suspend_timer.start(self.suspend_timeout)
    
    def _auto_suspend(self):
        """自動サスペンド処理"""
        self.suspend()
    
    def suspend(self):
        """レンダリングを停止してメモリを解放"""
        if not self.is_suspended:
            try:
                self.page().setLifecycleState(
                    QWebEnginePage.LifecycleState.Discarded
                )
                self.is_suspended = True
                self.suspend_timer.stop()
                self.suspended.emit(True)
                print(f"WebView サスペンド: {self.url().toString()}")
            except Exception as e:
                print(f"サスペンド失敗: {e}")
    
    def resume(self):
        """レンダリングを再開"""
        if self.is_suspended:
            try:
                self.page().setLifecycleState(
                    QWebEnginePage.LifecycleState.Active
                )
                self.is_suspended = False
                self._reset_suspend_timer()
                self.suspended.emit(False)
                print(f"WebView 再開: {self.url().toString()}")
            except Exception as e:
                print(f"再開失敗: {e}")
    
    def set_suspend_timeout(self, timeout_ms: int):
        """サスペンドタイムアウトを設定（ミリ秒）"""
        self.suspend_timeout = timeout_ms
        if self.suspend_timer.isActive():
            self._reset_suspend_timer()
    
    def showEvent(self, event):
        """表示時に自動的に再開"""
        super().showEvent(event)
        if self.is_suspended:
            self.resume()
        else:
            self._reset_suspend_timer()
    
    def hideEvent(self, event):
        """非表示時にタイマーを停止"""
        super().hideEvent(event)
        self.suspend_timer.stop()


class LazyWebView(QWidget):
    """遅延ロード機能を持つWebViewラッパー"""
    
    loaded = Signal()  # ロード完了シグナル
    
    def __init__(self, url: str, profile: QWebEngineProfile, parent=None):
        super().__init__(parent)
        
        self.url = url
        self.profile = profile
        self.web_view: SuspendableWebView = None
        self.is_loaded = False
        
        # レイアウトの準備
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
    
    def load_content(self):
        """コンテンツを遅延ロード"""
        if not self.is_loaded:
            print(f"遅延ロード開始: {self.url}")
            
            # WebViewを作成
            self.web_view = SuspendableWebView(self.profile, self)
            self.web_view.setUrl(QUrl(self.url))
            
            # レイアウトに追加
            self.layout.addWidget(self.web_view)
            
            self.is_loaded = True
            self.loaded.emit()
        
        return self.web_view
    
    def get_web_view(self) -> SuspendableWebView:
        """WebViewを取得（未ロードの場合はロード）"""
        if not self.is_loaded:
            self.load_content()
        return self.web_view
    
    def is_view_loaded(self) -> bool:
        """ロード済みかどうかを確認"""
        return self.is_loaded
    
    def suspend(self):
        """WebViewをサスペンド"""
        if self.is_loaded and self.web_view:
            self.web_view.suspend()
    
    def resume(self):
        """WebViewを再開"""
        if self.is_loaded and self.web_view:
            self.web_view.resume()
