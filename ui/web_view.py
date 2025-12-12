"""
AI比較アプリケーション - カスタムWebビューモジュール
メモリ最適化機能を備えたWebViewコンポーネント
"""

from PySide6.QtCore import QUrl, QTimer, Signal, Qt
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class CustomWebEnginePage(QWebEnginePage):
    """ポップアップウィンドウをサポートするカスタムWebEnginePage"""
    
    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)
    
    def createWindow(self, window_type):
        """新しいウィンドウ/タブを作成（Googleログインのポップアップ対応）"""
        # 親ウィンドウとなるコンテナを作成
        popup = QWidget()
        popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        popup.setWindowTitle("ダウンロード中－完了後に自動で閉じます")
        popup.resize(600, 750)
        
        layout = QVBoxLayout(popup)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # URL表示用ラベル（セキュリティ対策）
        url_label = QLabel("URL: Loading...")
        url_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                color: #333;
                padding: 8px;
                border-bottom: 1px solid #ccc;
                font-family: monospace;
            }
        """)
        layout.addWidget(url_label)
        
        # 新しいページとビューを作成
        page = CustomWebEnginePage(self.profile(), popup)
        view = QWebEngineView(popup)
        view.setPage(page)
        
        # URL変更時にラベルを更新（長すぎる場合は省略）
        def update_url_label(url):
            try:
                url_str = url.toString()
                if len(url_str) > 150:
                    url_str = url_str[:150] + "..."
                url_label.setText(f"URL: {url_str}")
            except RuntimeError:
                # ウィンドウが閉じられてラベルが削除された場合に発生するエラーを無視
                pass
            
        view.urlChanged.connect(update_url_label)
        
        layout.addWidget(view)
        
        # ウィンドウを表示
        popup.show()
        
        # ウィンドウへの参照を保持してGCを防ぐ
        if not hasattr(self, '_popups'):
            self._popups = []
        self._popups.append(popup)
        
        # ダウンロード完了時にウィンドウを自動で閉じる
        from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
        
        def handle_download(download_item):
            # このページからのダウンロードリクエストか確認
            # 注意: download_item.page() が None の場合もあるため安全策をとる
            if download_item.page() == page:
                def on_state_changed(state):
                    if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                        # 少し遅延させてから閉じる（完了の余韻）
                        QTimer.singleShot(1000, popup.close)
                
                download_item.stateChanged.connect(on_state_changed)
        
        # プロファイルのシグナルに接続
        # 注意: 厳密にはdisconnectが必要だが、popupが消えればハンドラもGCされることを期待
        # ただしプロファイルは長生きするので、ハンドラが残り続けるリスクがある。
        # 接続オブジェクトを保持して、popup破棄時に切断するのが正しい。
        conn = self.profile().downloadRequested.connect(handle_download)
        
        # ウィンドウが閉じられたらリストから削除 & シグナル切断
        def cleanup():
            if popup in self._popups:
                self._popups.remove(popup)
            self.profile().downloadRequested.disconnect(conn)
            
        popup.destroyed.connect(cleanup)
        
        return page
        




class SuspendableWebView(QWebEngineView):
    """サスペンド機能を持つWebView"""
    
    suspended = Signal(bool)  # サスペンド状態変更シグナル
    
    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(parent)
        
        # プロファイルの設定（カスタムページを使用）
        # プロファイルの設定（カスタムページを使用）
        page = CustomWebEnginePage(profile, self)
        
        # ユーザー操作なしでの動画再生を許可（Sora等）
        page.settings().setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        
        self.setPage(page)
        
        # サスペンド管理
        self.is_suspended = False
        self.suspend_timer = QTimer(self)
        self.suspend_timer.timeout.connect(self._auto_suspend)
        self.suspend_timeout = 300000  # 5分（ミリ秒）
        
        # ロードタイムアウト管理（Adobe Express対策）
        self.load_timeout_timer = QTimer(self)
        self.load_timeout_timer.setSingleShot(True)
        self.load_timeout_timer.timeout.connect(self._on_load_timeout)
        self.load_timeout_duration = 30000  # 30秒
        
        # イベント接続
        self.loadStarted.connect(self._on_load_started)
        self.loadProgress.connect(self._on_load_progress)
        self.loadFinished.connect(self._on_load_finished)
        self.renderProcessTerminated.connect(self._on_render_process_terminated)
    
    def _on_load_started(self):
        """ページロード開始時の処理"""
        print(f"Load started: {self.url().toString()}")
        self.load_timeout_timer.start(self.load_timeout_duration)
    
    def _on_load_progress(self, progress):
        """ページロード進行状況の処理"""
        if progress > 0 and progress < 100:
            self.load_timeout_timer.start(self.load_timeout_duration)
    
    def _on_load_timeout(self):
        """ロードタイムアウト時の処理"""
        print(f"⚠️ Load timeout - Auto reload: {self.url().toString()}")
        self.load_timeout_timer.stop()
        QTimer.singleShot(500, self.reload)
    
    def _on_render_process_terminated(self, termination_status, exit_code):
        """レンダリングプロセスクラッシュ時の処理"""
        print(f"Render process terminated - Auto reload")
        QTimer.singleShot(1000, self.reload)
    
    def _on_load_finished(self, ok):
        """ページロード完了時の処理"""
        self.load_timeout_timer.stop()
        if ok:
            print(f"✓ Load finished: {self.url().toString()}")
            self._reset_suspend_timer()
        else:
            print(f"✗ Load failed: {self.url().toString()}")
    
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
                # Adobe Express等の複雑なアプリでは、リロードすると状態が壊れるため
                # エラー時でもリロードしない
    
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
