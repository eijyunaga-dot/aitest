"""
AI比較アプリケーション - メインウィンドウモジュール
"""

import psutil
import webbrowser
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar,
    QLabel, QStyle, QToolButton, QHBoxLayout, QWidget
)

from .comparison_widget import AIComparisonWidget
from .comparison_widget import AIComparisonWidget
from .web_editor_widget import WebEditorWidget
from .sora_widget import SoraWidget
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
        self._create_statusbar()
        self._create_tab_corner_controls()  # タブバー右端にナビゲーションコントロールを配置
        
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
        self.tab_widget.addTab(self.text_ai_widget, "AIアシスタント")
        
        # 画像AI比較タブ
        image_ai_services = self.ai_manager.get_all_image_ai_services()
        self.image_ai_widget = AIComparisonWidget(
            image_ai_services, 
            self.settings, 
            self,
            custom_sizes=[2, 1]  # ImageFX:DeepL = 2:1
        )
        self.tab_widget.addTab(self.image_ai_widget, "音楽や動画など(Test版)")
        
        # 音声要約などタブ
        audio_ai_services = self.ai_manager.get_all_audio_ai_services()
        self.audio_ai_widget = AIComparisonWidget(
            audio_ai_services, 
            self.settings, 
            self
        )
        self.tab_widget.addTab(self.audio_ai_widget, "音声や資料の要約")
        
        # 動画生成AIタブ（タブ4）
        # 動画生成AIタブ（タブ4）
        # Sora専用のWebView2ランチャーを使用
        self.video_ai_widget = SoraWidget(self)
        self.tab_widget.addTab(self.video_ai_widget, "動画生成")
        
        # 開発者AIタブ（タブ5）
        developer_ai_services = self.ai_manager.get_all_developer_ai_services()
        self.developer_ai_widget = AIComparisonWidget(
            developer_ai_services, 
            self.settings, 
            self
        )
        self.tab_widget.addTab(self.developer_ai_widget, "開発者用")
        
        # 画像編集(WEB)タブ - 外部ブラウザで開くボタン
        self.web_editor_widget = WebEditorWidget(self)
        self.tab_widget.addTab(self.web_editor_widget, "画像編集(WEB)")
        
        # 中央ウィジェットとして設定
        self.setCentralWidget(self.tab_widget)
        
        # 最初のタブを初期化
        self.text_ai_widget.initialize_views()
    
    def _create_tab_corner_controls(self):
        """タブバー右側のコントロールを作成"""
        corner_widget = QWidget()
        layout = QHBoxLayout(corner_widget)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(4)
        
        # 説明文ラベル
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 11px; color: #A0A0A0; padding: 0 10px;")
        layout.addWidget(self.title_label)
        
        # ボタンスタイル
        btn_style = """
            QToolButton {
                background-color: #3A3A3A;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 4px;
                color: #FFFFFF;
            }
            QToolButton:hover {
                background-color: #4A7BD8;
                border: 1px solid #5B8DEE;
            }
            QToolButton:pressed {
                background-color: #3A6BC8;
            }
        """
        
        # 戻るボタン
        back_btn = QToolButton()
        back_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        back_btn.setToolTip("戻る")
        back_btn.clicked.connect(self._go_back)
        back_btn.setStyleSheet(btn_style)
        layout.addWidget(back_btn)
        
        # 進むボタン
        forward_btn = QToolButton()
        forward_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        forward_btn.setToolTip("進む")
        forward_btn.clicked.connect(self._go_forward)
        forward_btn.setStyleSheet(btn_style)
        layout.addWidget(forward_btn)
        
        # 更新ボタン
        reload_btn = QToolButton()
        reload_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        reload_btn.setToolTip("更新")
        reload_btn.clicked.connect(self._reload)
        reload_btn.setStyleSheet(btn_style)
        layout.addWidget(reload_btn)
        
        # 音量ミュートボタン（強調カラー）
        volume_btn_style = """
            QToolButton {
                background-color: #10a37f;
                border: 1px solid #0d8a6a;
                border-radius: 3px;
                padding: 4px 8px;
                color: #FFFFFF;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #0d8a6a;
                border: 1px solid #0a7559;
            }
            QToolButton:pressed {
                background-color: #0a7559;
            }
        """
        
        self.volume_btn = QToolButton()
        self.volume_btn.setText("🔊")
        self.volume_btn.setToolTip("音量ミュート/アンミュート")
        self.volume_btn.setStyleSheet(volume_btn_style)
        self.volume_btn.clicked.connect(self._toggle_mute)
        layout.addWidget(self.volume_btn)
        
        # 音量制御の初期化
        self._init_volume_control()
        
        # コーナーウィジェットとしてタブバーの右端に設定
        self.tab_widget.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)
        
        # 初期説明文を設定
        self._update_title_description()
    
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
                elif isinstance(widget, WebEditorWidget):
                    widget.on_tab_hide()
        
        # 現在のタブを表示処理
        current_widget = self.tab_widget.widget(index)
        if isinstance(current_widget, AIComparisonWidget):
            current_widget.on_tab_show()
        elif isinstance(current_widget, WebEditorWidget):
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
            text = "🎙️登録した資料の中からのみ検索、流出の心配なし"
        elif current_index == 3:  # 動画生成AIタブ
            text = "🎥 Sora (動画生成) | アクセス権限が必要です"
        elif current_index == 4:  # 開発者AIタブ
            text = "🔧 Google AI Studio (開発者向け) | APIキーの管理に注意"
        else:
            text = "adobeは不安定なのでブラウザショートカットにしました"
        
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
    
    def _init_volume_control(self):
        """音量制御の初期化"""
        self.volume_interface = None
        self.is_muted = False
        try:
            # pycawを使ってデフォルトスピーカーを取得
            devices = AudioUtilities.GetSpeakers()
            
            # 内部のCOMデバイスにアクセス
            interface = devices._dev.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            
            # 初期状態を取得
            self.is_muted = bool(self.volume_interface.GetMute())
            self._update_volume_button()
            
        except Exception as e:
            print(f"Volume control init error: {e}")
            self.volume_interface = None
    
    def _toggle_mute(self):
        """ミュート状態をトグル"""
        if self.volume_interface:
            try:
                self.is_muted = not self.is_muted
                self.volume_interface.SetMute(self.is_muted, None)
                self._update_volume_button()
            except Exception as e:
                print(f"Mute toggle error: {e}")
    
    def _update_volume_button(self):
        """ボタンの表示を更新"""
        if self.volume_interface:
            try:
                self.is_muted = self.volume_interface.GetMute()
            except:
                pass
        
        if self.is_muted:
            self.volume_btn.setText("🔇")
            self.volume_btn.setStyleSheet("""
                QToolButton {
                    background-color: #dc3545;
                    border: 1px solid #c82333;
                    border-radius: 3px;
                    padding: 4px 8px;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #c82333;
                }
            """)
        else:
            self.volume_btn.setText("🔊")
            self.volume_btn.setStyleSheet("""
                QToolButton {
                    background-color: #10a37f;
                    border: 1px solid #0d8a6a;
                    border-radius: 3px;
                    padding: 4px 8px;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #0d8a6a;
                }
            """)
    
    def closeEvent(self, event):
        """ウィンドウを閉じる時の処理"""
        self._save_geometry()
        event.accept()
