"""
AI比較アプリケーション - メインエントリーポイント

PySide6とQWebEngineViewを使用して、複数のAIアシスタントサービスを
同時に表示・比較するデスクトップアプリケーション
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """アプリケーションのメインエントリーポイント"""
    
    # High DPIスケーリングを有効化
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Adobe Express対策: Chromiumのフラグ設定
    # SharedArrayBuffer, WebAssemblyThreads（エディタ画面で必要）, セキュリティ制限の緩和, GPU高速化
    import os
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--enable-features=SharedArrayBuffer,WebAssemblyThreads "
        "--disable-web-security "
        "--allow-running-insecure-content "
        "--disable-features=BlockInsecurePrivateNetworkRequests "
        "--ignore-gpu-blocklist "
        "--enable-gpu-rasterization "
        "--renderer-process-limit=20 "
        "--js-flags=--max-old-space-size=4096 "
        "--disable-web-gl-image-chromium"
    )
    
    # アプリケーションの作成
    app = QApplication(sys.argv)
    app.setApplicationName("AI比較アプリケーション")
    app.setOrganizationName("AI Comparison")
    
    # メインウィンドウの作成と表示
    window = MainWindow()
    window.showMaximized()  # 1366x768解像度でも最適に表示
    
    # イベントループの開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
