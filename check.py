import os
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

# ログ出力用関数（我が隊の通信規律）
def mission_log(log_type, message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] [{log_type}] {message}")

def load_proxy_url(json_path):
    if not os.path.exists(json_path):
        mission_log("ERROR", f"設定ファイルが見つかりません: {json_path}")
        return None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # proxy_urlを取得
            return data.get("proxy_url")
    except Exception as e:
        mission_log("ERROR", f"JSONの読み込みに失敗しました: {e}")
        return None

def main():
    json_path = "./urls.json"
    last_url = None
    last_status = None
    
    mission_log("SYSTEM", "定期リクエストミッションを開始します！(1分間隔)")

    while True:
        current_url = load_proxy_url(json_path) + "/json?url="
        
        if current_url:
            # 値（URL）が変わったときにログに出す
            if current_url != last_url:
                mission_log("UPDATE", f"対象URLが変更されました: {last_url} -> {current_url}")
                last_url = current_url
                # URLが変わったらステータス記録もリセット
                last_status = None

            try:
                mission_log("ACTION", f"リクエスト送信中: {current_url}")
                # タイムアウトは15秒に設定
                with urllib.request.urlopen(current_url, timeout=15) as response:
                    status_code = response.getcode()
                    
                    # 状態が変わったとき（または初回）にログを出す
                    if status_code != last_status:
                        mission_log("SUCCESS", f"リクエスト成功！ ステータスコード: {status_code}")
                        last_status = status_code
                        
            except urllib.error.HTTPError as e:
                if e.code != last_status:
                    mission_log("WARNING", f"HTTPエラーが発生しました。ステータス: {e.code}")
                    last_status = e.code
            except urllib.error.URLError as e:
                if "timeout" in str(e).lower():
                    status_str = "TIMEOUT"
                else:
                    status_str = "URL_ERROR"
                    
                if status_str != last_status:
                    mission_log("ERROR", f"接続エラーが発生しました: {e.reason}")
                    last_status = status_str
            except Exception as e:
                if "UNKNOWN" != last_status:
                    mission_log("CRITICAL", f"予期せぬエラーが発生しました: {e}")
                    last_status = "UNKNOWN"
        else:
            if last_url is not None:
                mission_log("WARNING", "urls.json から proxy_url が取得できないか、ファイルが空です。")
                last_url = None
                last_status = None

        # 1分間（60秒）待機
        time.sleep(60)

if __name__ == "__main__":
    main()
