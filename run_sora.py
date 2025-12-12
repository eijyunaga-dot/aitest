import webview
import sys
import os

# 埋め込み用に特定のタイトルを使用
WINDOW_TITLE = "SoraWebView2Container"

def main():
    url = "https://sora.chatgpt.com/"
    
    # 埋め込み用のウィンドウを作成
    # frameless=True: タイトルバーなし（埋め込み時に邪魔にならないように）
    # easy_drag=False: ドラッグ移動を無効化（埋め込み後に動かされると困るため）
    window = webview.create_window(
        WINDOW_TITLE, 
        url,
        width=1200,
        height=800,
        frameless=True,
        easy_drag=False
    
    )
    
    # GUIバックエンドをEdge (WebView2) に明示的に指定
    # debug=False: F12開発者ツール無効（本番用）
    webview.start(debug=False, gui='edgechromium')

if __name__ == '__main__':
    main()
