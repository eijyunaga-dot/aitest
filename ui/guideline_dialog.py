"""
AI利用ガイドラインダイアログ
起動時に表示し、同意した場合のみメイン画面を表示
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget, QFrame
)



class GuidelineDialog(QDialog):
    """AI利用ガイドラインダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI利用ガイドライン")
        self.setMinimumSize(500, 600)  # 縦長レイアウト
        self.setModal(True)
        
        self._init_ui()
        self._apply_stylesheet()
    
    def _init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # タイトル
        title_label = QLabel("AI利用ガイドライン 10の原則")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Yu Gothic UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("padding: 15px; background-color: #2D2D2D; color: #E0E0E0;")
        layout.addWidget(title_label)
        
        subtitle = QLabel("経済産業省「AI事業者ガイドライン（第1.0版）」に基づく")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("padding: 5px; background-color: #2D2D2D; color: #A0A0A0; font-size: 11px;")
        layout.addWidget(subtitle)
        
        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(10)
        
        # 10原則
        principles = [
            ("1. 人間中心", "AIは人間の尊厳と自律を尊重し、偽情報対策を行い多様性を確保する", "👤"),
            ("2. 安全性", "人間の生命・心身・財産、および環境への配慮と適正な利用・学習を行う", "🛡️"),
            ("3. 公平性", "AIモデルに含まれるバイアス(偏見)に配慮し、必要に応じて人間が判断に介在する", "⚖️"),
            ("4. プライバシー保護", "個人情報やプライバシーを保護し、関係法令を遵守する", "🔒"),
            ("5. セキュリティ確保", "不正操作によるAIの改変や停止を防ぎ、最新の脅威に対応する", "🔐"),
            ("6. 透明性", "検証可能性を確保し、ステークホルダーへ適切な情報提供と説明を行う", "🔍"),
            ("7. アカウンタビリティ", "責任者を明確にし、トレーサビリティを確保して文書化する", "📋"),
            ("8. 教育・リテラシー", "AIリテラシーを身につけ、継続的な学習とリスキリングを行う", "📚"),
            ("9. 公正競争確保", "公正な競争環境を維持し、独占的な行為を避ける", "🤝"),
            ("10. イノベーション", "オープンイノベーションを推進し、相互運用性に配慮して革新を促進", "💡"),
        ]
        
        for title, desc, icon in principles:
            item = self._create_principle_item(icon, title, desc)
            content_layout.addWidget(item)
        
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 15, 20, 15)
        button_layout.setSpacing(15)
        
        disagree_btn = QPushButton("同意しない")
        disagree_btn.setMinimumSize(120, 40)
        disagree_btn.clicked.connect(self.reject)
        
        agree_btn = QPushButton("同意する")
        agree_btn.setMinimumSize(120, 40)
        agree_btn.setObjectName("agreeButton")
        agree_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(disagree_btn)
        button_layout.addWidget(agree_btn)
        
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setStyleSheet("background-color: #2D2D2D;")
        layout.addWidget(button_container)
    
    def _create_principle_item(self, icon: str, title: str, description: str) -> QWidget:
        """原則アイテムを作成"""
        item = QFrame()
        item.setFrameShape(QFrame.Shape.StyledPanel)
        item.setStyleSheet("""
            QFrame {
                background-color: #3A3A3A;
                border: 1px solid #505050;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        
        # アイコン
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setFixedWidth(40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # テキスト
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Yu Gothic UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #5B9BD5; border: none;")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #E0E0E0; font-size: 12px; border: none;")
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout, 1)
        
        return item
    
    def _apply_stylesheet(self):
        """スタイルシートの適用"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QScrollArea {
                background-color: #1E1E1E;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2D2D2D;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #505050;
                min-height: 30px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #606060;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QPushButton {
                background-color: #3A3A3A;
                border: 1px solid #505050;
                border-radius: 5px;
                padding: 10px 20px;
                color: #E0E0E0;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                border: 1px solid #606060;
            }
            QPushButton#agreeButton {
                background-color: #4A7BD8;
                border: 1px solid #5B8DEE;
            }
            QPushButton#agreeButton:hover {
                background-color: #5B8DEE;
            }
        """)
