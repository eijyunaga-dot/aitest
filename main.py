"""
AI比較アプリケーション - メインエントリーポイント

PySide6とQWebEngineViewを使用して、複数のAIアシスタントサービスを
同時に表示・比較するデスクトップアプリケーション
"""

import sys
import os
import traceback

# Setup exception logging
try:
    log_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), 'main_debug.log')
    if os.path.exists(log_path):
        os.remove(log_path)
except:
    pass

def exception_hook(exctype, value, tb):
    log_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), 'main_debug.log')
    with open(log_path, 'a') as f:
        f.write("Unhandled exception:\n")
        traceback.print_exception(exctype, value, tb, file=f)

sys.excepthook = exception_hook

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Import UI components inside try-except block in main if possible, 
# but for now we keep them here as they are top-level. 
# The excepthook should catch import errors if they happen after hook setup.
from ui.main_window import MainWindow
from ui.guideline_dialog import GuidelineDialog


def main():
    """アプリケーションのメインエントリーポイント"""
    
    # High DPIスケーリングを有効化
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Chromiumのフラグ設定（GPU高速化のみ維持）
    import os
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--ignore-gpu-blocklist "
        "--enable-gpu-rasterization "
        "--enable-features=PlatformHEVCDecoderSupport,ProprietaryCodecs,ms-playready "
        "--autoplay-policy=no-user-gesture-required "
        "--enable-widevine"
    )
    
    # アプリケーションの作成
    app = QApplication(sys.argv)
    app.setApplicationName("AI比較アプリケーション")
    app.setOrganizationName("AI Comparison")
    
    # ガイドラインダイアログを表示（毎回表示）
    dialog = GuidelineDialog()
    if dialog.exec() != dialog.DialogCode.Accepted:
        # 同意しない場合はアプリを終了
        sys.exit(0)
    
    # メインウィンドウの作成と表示
    window = MainWindow()
    window.showMaximized()  # 1366x768解像度でも最適に表示
    
    # イベントループの開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
