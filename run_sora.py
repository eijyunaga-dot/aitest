import webview
import sys
import os

# 埋め込み用に特定のタイトルを使用
WINDOW_TITLE = "SoraWebView2Container"

def main():
    try:
        # ログ設定
        log_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), 'sora_debug.log')
        
        # エラー発生時にログ出しするためのフック
        def exception_hook(exctype, value, traceback):
            with open(log_path, 'a') as f:
                import traceback as tb
                f.write(f"Unhandled exception:\n")
                tb.print_exception(exctype, value, traceback, file=f)
        sys.excepthook = exception_hook

        # WebView2の自動再生ポリシーを緩和（ユーザー操作なしで動画再生を許可）
        os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = "--autoplay-policy=no-user-gesture-required"

        url = "https://sora.chatgpt.com/"
        
        # 埋め込み用のウィンドウを作成
        window = webview.create_window(
            WINDOW_TITLE, 
            url,
            width=1200,
            height=800,
            frameless=True,
            easy_drag=False
        )
        
        # ユーザーデータ保存先の設定（ログイン情報の永続化）
        # %LOCALAPPDATA%\AI Comparison\AI比較アプリケーション\SoraProfile に保存
        local_app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        storage_path = os.path.join(local_app_data, 'AI Comparison', 'AI比較アプリケーション', 'SoraProfile')
        
        if not os.path.exists(storage_path):
            try:
                os.makedirs(storage_path, exist_ok=True)
            except:
                pass # 権限エラー等ならデフォルト動作に任せる

        # GUIバックエンドをEdge (WebView2) に明示的に指定
        webview.start(debug=False, gui='edgechromium', private_mode=False, storage_path=storage_path)
        
    except Exception as e:
        log_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), 'sora_critical.log')
        with open(log_path, 'w') as f:
            f.write(f"Critical error: {str(e)}")
            import traceback
            f.write(traceback.format_exc())

if __name__ == '__main__':
    main()
