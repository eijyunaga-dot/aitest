"""
AI比較アプリケーション - メインウィンドウモジュール
"""

import psutil
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QStatusBar,
    QLabel, QStyle
)

from .comparison_widget import AIComparisonWidget
from models.ai_service import AIServiceManager
from utils.settings import Settings


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    
    def __init__(self):
        super().__init__()
        
        # 設定とモデルの初期化
        self.settings = Settings()
        self.ai_manager = AIServiceManager()
        
        # ウィンドウ設定
        self.setWindowTitle("AI比較アプリケーション")
        self.setMinimumSize(1200, 720)  # 1366x768解像度に対応
        
        # UIの初期化
        self._init_ui()
        self._create_statusbar()  # ツールバーより先に作成
        self._create_toolbar()
        
        # ウィンドウジオメトリの復元
        self._restore_geometry()
        
        # メモリ監視タイマー
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self._update_memory_status)
        self.memory_timer.start(2000)  # 2秒ごとに更新
        
        # スタイルシートの適用
        self._apply_stylesheet()
    
    def _init_ui(self):
        """UIの初期化"""
        # タブウィジェットの作成
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # 文章AI比較タブ
        text_ai_services = self.ai_manager.get_all_text_ai_services()
        self.text_ai_widget = AIComparisonWidget(
            text_ai_services, 
            self.settings, 
            self
        )
        self.tab_widget.addTab(self.text_ai_widget, "文章AI")
        
        # 画像AI比較タブ
        image_ai_services = self.ai_manager.get_all_image_ai_services()
        self.image_ai_widget = AIComparisonWidget(
            image_ai_services, 
            self.settings, 
            self,
            custom_sizes=[2, 1]  # ImageFX:DeepL = 2:1
        )
        self.tab_widget.addTab(self.image_ai_widget, "画像ほかAI")
        
        # Gemini画像生成タブ
        gemini_image_services = self.ai_manager.get_all_gemini_image_services()
        self.gemini_image_widget = AIComparisonWidget(
            gemini_image_services, 
            self.settings, 
            self
        )
        self.tab_widget.addTab(self.gemini_image_widget, "AdobeExpress")
        
       # NotebookLMタブ
        audio_ai_services = self.ai_manager.get_all_audio_ai_services()
        self.audio_ai_widget = AIComparisonWidget(
            audio_ai_services, 
            self.settings, 
            self
        )
        self.tab_widget.addTab(self.audio_ai_widget, "音声要約など")
        
        # 中央ウィジェットとして設定
        self.setCentralWidget(self.tab_widget)
        
        # 最初のタブを初期化
        self.text_ai_widget.initialize_views()
    
    def _create_toolbar(self):
        """ツールバーの作成"""
        from PySide6.QtCore import QSize
        
        toolbar = QToolBar("メインツールバー")
        toolbar.setMovable(False)
        
        # アイコンサイズの設定（QSizeオブジェクトを使用）
        icon_size = self.style().pixelMetric(QStyle.PixelMetric.PM_SmallIconSize)
        toolbar.setIconSize(QSize(icon_size, icon_size))
        self.addToolBar(toolbar)
        
        # 戻るボタン
        back_action = QAction("戻る", self)
        back_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        back_action.triggered.connect(self._go_back)
        toolbar.addAction(back_action)
        
        # 進むボタン
        forward_action = QAction("進む", self)
        forward_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        forward_action.triggered.connect(self._go_forward)
        toolbar.addAction(forward_action)
        
        # 更新ボタン
        reload_action = QAction("更新", self)
        reload_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        reload_action.triggered.connect(self._reload)
        toolbar.addAction(reload_action)
        
        toolbar.addSeparator()
        
        # タイトルラベル（中央） - タブに応じて説明文が変わる
        toolbar.addWidget(QLabel())  # スペーサー
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 12px; color: #E0E0E0; padding: 0 20px;")
        toolbar.addWidget(self.title_label)
        
        # 初期説明文を設定
        self._update_title_description()
        
        self.toolbar = toolbar
    
    def _create_statusbar(self):
        """ステータスバーの作成"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        
        # 接続状態ラベル
        self.status_label = QLabel("準備完了")
        statusbar.addWidget(self.status_label)
        
        # メモリ使用量ラベル
        self.memory_label = QLabel()
        statusbar.addPermanentWidget(self.memory_label)
        
        self._update_memory_status()
    
    def _apply_stylesheet(self):
        """スタイルシートの適用"""
        qss = """
        QMainWindow {
            background-color: #1E1E1E;
        }
        
        QToolBar {
            background-color: #2D2D2D;
            border-bottom: 1px solid #404040;
            spacing: 8px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: #3A3A3A;
            border: 1px solid #505050;
            border-radius: 4px;
            padding: 8px;
            color: #FFFFFF;
        }
        
        QToolButton:hover {
            background-color: #4A7BD8;
            border: 1px solid #5B8DEE;
        }
        
        QToolButton:pressed {
            background-color: #3A6BC8;
            border: 1px solid #4A7BD8;
        }
        
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #1E1E1E;
        }
        
        QTabBar::tab {
            background-color: #2D2D2D;
            color: #A0A0A0;
            padding: 10px 20px;
            border: none;
            border-bottom: 3px solid transparent;
            min-width: 120px;
        }
        
        QTabBar::tab:selected {
            color: #E0E0E0;
            border-bottom: 3px solid #5B8DEE;
        }
        
        QTabBar::tab:hover {
            background-color: #3A3A3A;
        }
        
        QStatusBar {
            background-color: #2D2D2D;
            border-top: 1px solid #404040;
            color: #A0A0A0;
        }
        
        QLabel {
            color: #E0E0E0;
        }
        """
        self.setStyleSheet(qss)
    
    def _on_tab_changed(self, index: int):
        """タブ切り替え時の処理"""
        # 前のタブを非表示処理
        for i in range(self.tab_widget.count()):
            if i != index:
                widget = self.tab_widget.widget(i)
                if isinstance(widget, AIComparisonWidget):
                    widget.on_tab_hide()
        
        # 現在のタブを表示処理
        current_widget = self.tab_widget.widget(index)
        if isinstance(current_widget, AIComparisonWidget):
            current_widget.on_tab_show()
        
        # 説明文を更新
        self._update_title_description()
        self._update_status_message()
    
    def _go_back(self):
        """戻る"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, AIComparisonWidget):
            current_widget.go_back_all()
    
    def _go_forward(self):
        """進む"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, AIComparisonWidget):
            current_widget.go_forward_all()
    
    def _reload(self):
        """更新"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, AIComparisonWidget):
            current_widget.reload_all()
    
    def _update_memory_status(self):
        """メモリ使用状況を更新"""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # メモリ警告の確認
            threshold = self.settings.get('memory_warning_threshold', 6144)
            if memory_mb > threshold:
                color = "#FF9800"  # 警告色
                status = "⚠️"
            else:
                color = "#4CAF50"  # 成功色
                status = "✓"
            
            self.memory_label.setText(
                f"{status} メモリ: {memory_mb:.0f} MB"
            )
            self.memory_label.setStyleSheet(f"color: {color}; font-size: 11px;")
        except Exception as e:
            self.memory_label.setText(f"メモリ: N/A")
    
    def _update_status_message(self):
        """ステータスメッセージを更新"""
        if not hasattr(self, 'status_label'):
            return  # ステータスバーがまだ作成されていない場合はスキップ
            
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, AIComparisonWidget):
            info = current_widget.get_memory_info()
            msg = (f"ビュー: {info['loaded_views']}/{info['total_views']} ロード済 | "
                   f"{info['suspended_views']} サスペンド中")
            self.status_label.setText(msg)
    
    def _update_title_description(self):
        """タブに応じた説明文を更新"""
        if not hasattr(self, 'title_label'):
            return  # タイトルラベルがまだ作成されていない場合はスキップ
        
        current_index = self.tab_widget.currentIndex()
        
        if current_index == 0:  # 文章AIタブ
            text = "💡 初回のみログイン必要 | 保存は[ダウンロード]フォルダ固定"
        elif current_index == 1:  # 画像AIタブ
            text = "🎨 命令文は英語のみなのでDeepLで翻訳コピペ"
        elif current_index == 2:  # 音声AIタブ
            text = "無料版は「月間10トークン」なのでご利用は計画的に"
        else:
            text = "🎙️ NotebookLM:音声要約とか登録資料の辞書化など"
        
        self.title_label.setText(text)
    
    def _restore_geometry(self):
        """ウィンドウジオメトリの復元"""
        geometry = self.settings.get('window_geometry')
        if geometry:
            # 実装は省略（必要に応じてQByteArrayから復元）
            pass
    
    def _save_geometry(self):
        """ウィンドウジオメトリの保存"""
        # 実装は省略（必要に応じてQByteArrayとして保存）
        pass
    
    def closeEvent(self, event):
        """ウィンドウを閉じる時の処理"""
        self._save_geometry()
        event.accept()
