import sys
import os
import subprocess
import ctypes
from ctypes import wintypes
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer

# Win32 API 定義
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# 定数
GWL_STYLE = -16
WS_CHILD = 0x40000000
WS_POPUP = 0x80000000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000

class SoraWidget(QWidget):
    """
    Sora起動用ウィジェット
    WebView2 (pywebview) プロセスを起動し、そのウィンドウをSetParentで埋め込む
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.process = None
        self.hwnd_sora = 0
        self.is_embedded = False
        self.foreign_thread_id = 0
        self.my_thread_id = 0
        self.threads_attached = False
        
        # フォーカスポリシーを設定
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # UI初期化（ロード中の表示）
        layout = QVBoxLayout(self)
        self.status_label = QLabel("Initializing WebView2 for Sora...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # プロセス起動
        self._launch_process()
        
        # ウィンドウ検索タイマー
        self.search_timer = QTimer(self)
        self.search_timer.timeout.connect(self._search_window)
        self.search_timer.start(500)
    
    def _launch_process(self):
        """別プロセスでRun Soraスクリプトを起動"""
        try:
            script_path = os.path.join(os.getcwd(), 'run_sora.py')
            creationflags = 0x08000000  # CREATE_NO_WINDOW
            
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                creationflags=creationflags
            )
        except Exception as e:
            self.status_label.setText(f"Error launching process: {str(e)}")

    def _search_window(self):
        """ターゲットウィンドウを探す"""
        target_title = "SoraWebView2Container"
        hwnd = user32.FindWindowW(None, target_title)
        
        if hwnd and hwnd != 0:
            self.hwnd_sora = hwnd
            self.search_timer.stop()
            self._embed_window()
            
    def _embed_window(self):
        """ウィンドウを埋め込む"""
        if not self.hwnd_sora:
            return
            
        try:
            my_hwnd = int(self.winId())
            
            # スレッドIDを取得して入力キューを接続
            self.foreign_thread_id = user32.GetWindowThreadProcessId(self.hwnd_sora, None)
            self.my_thread_id = kernel32.GetCurrentThreadId()
            
            # 入力スレッドを接続（これによりSetFocusが動作する）
            if self.foreign_thread_id != self.my_thread_id:
                user32.AttachThreadInput(self.foreign_thread_id, self.my_thread_id, True)
                self.threads_attached = True
            
            # 親ウィンドウを変更
            user32.SetParent(self.hwnd_sora, my_hwnd)
            
            # スタイルを変更
            style = user32.GetWindowLongW(self.hwnd_sora, GWL_STYLE)
            style = style & ~WS_POPUP | WS_CHILD
            style = style & ~WS_CAPTION & ~WS_THICKFRAME
            user32.SetWindowLongW(self.hwnd_sora, GWL_STYLE, style)
            
            self._update_window_position()
            
            self.is_embedded = True
            self.status_label.hide()
            
            # フォーカスを渡す
            self._give_focus()
            
        except Exception as e:
            self.status_label.setText(f"Embedding error: {e}")
            self.status_label.show()
    
    def _give_focus(self):
        """WebView2ウィンドウにフォーカスを渡す"""
        if self.hwnd_sora and user32.IsWindow(self.hwnd_sora):
            user32.SetForegroundWindow(self.hwnd_sora)
            user32.SetFocus(self.hwnd_sora)

    def _update_window_position(self):
        """子ウィンドウのサイズを合わせる"""
        if self.hwnd_sora and user32.IsWindow(self.hwnd_sora):
            user32.MoveWindow(
                self.hwnd_sora, 
                0, 0, 
                self.width(), self.height(), 
                True
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.is_embedded:
            self._update_window_position()
    
    def mousePressEvent(self, event):
        """クリックされたらフォーカスをWebViewに渡す"""
        if self.is_embedded:
            self._give_focus()
        super().mousePressEvent(event)
        
    def focusInEvent(self, event):
        """フォーカスを得たらWebViewに渡す"""
        if self.is_embedded:
            self._give_focus()
        super().focusInEvent(event)

    def closeEvent(self, event):
        """終了時の処理"""
        # スレッド入力の切断
        if self.threads_attached:
            user32.AttachThreadInput(self.foreign_thread_id, self.my_thread_id, False)
            
        # プロセスを終了させる
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
        super().closeEvent(event)
        
    def __del__(self):
        if self.process:
            try:
                self.process.kill()
            except:
                pass
