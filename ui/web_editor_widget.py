"""
画像編集(WEB)タブ - 外部ブラウザで開くボタンを提供
"""

import webbrowser
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class WebEditorWidget(QWidget):
    """外部Webエディタを開くためのウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # タイトルラベル
        title_label = QLabel("画像編集ツールを外部ブラウザで開く\n(作成した画像をポスター等に加工したり、月間10トークン分のAI生成もできます)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #E0E0E0;
                margin-bottom: 30px;
            }
        """)
        layout.addWidget(title_label)
        
        # Adobe Expressボタン
        express_btn = QPushButton("Adobe Expressを開く")
        express_btn.setFixedSize(300, 60)
        express_btn.setStyleSheet("""
            QPushButton {
                background-color: #5B9BD5;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4A8BC2;
            }
            QPushButton:pressed {
                background-color: #3A7AB0;
            }
        """)
        express_btn.clicked.connect(self._open_adobe_express)
        layout.addWidget(express_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # スペーサー
        layout.addSpacing(20)
        
        # Adobe Fireflyボタン
        firefly_btn = QPushButton("Adobe Fireflyを開く")
        firefly_btn.setFixedSize(300, 60)
        firefly_btn.setStyleSheet("""
            QPushButton {
                background-color: #E67E22;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #D35400;
            }
            QPushButton:pressed {
                background-color: #BA4A00;
            }
        """)
        firefly_btn.clicked.connect(self._open_adobe_firefly)
        layout.addWidget(firefly_btn, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def _open_adobe_express(self):
        """Adobe Expressを外部ブラウザで開く"""
        webbrowser.open("https://new.express.adobe.com/")
    
    def _open_adobe_firefly(self):
        """Adobe Fireflyを外部ブラウザで開く"""
        webbrowser.open("https://firefly.adobe.com/")
    
    # AIComparisonWidgetとの互換性のためのメソッド
    def on_tab_show(self):
        """タブが表示された時の処理（何もしない）"""
        pass
    
    def on_tab_hide(self):
        """タブが非表示になった時の処理（何もしない）"""
        pass
