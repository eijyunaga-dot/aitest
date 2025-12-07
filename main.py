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
    
    # Chromiumのフラグ設定（GPU高速化のみ維持）
    import os
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--ignore-gpu-blocklist "
        "--enable-gpu-rasterization"
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
