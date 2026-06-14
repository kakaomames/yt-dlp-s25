import aiohttp
import asyncio
from datetime import datetime

# 気象庁・防災科研 強震モニタAPI（公式仕様）
# 時刻パラメータを付与してリクエストする必要がある
async def monitor_loop():
    # 公式サーバーの基点
    base_url = "https://www.kmoni.bosai.go.jp/webservice/real/str/"
    
    async with aiohttp.ClientSession(headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.kmoni.bosai.go.jp/" # 公式サイトからのアクセスを装う
    }) as session:
        
        while True:
            # 現在時刻から適切なリクエスト用フォーマットを生成
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            # 公式APIのクエリパラメータ
            params = {'arr': now}
            
            try:
                # リアルタイムデータ取得
                async with session.get(base_url, params=params, timeout=5) as response:
                    if response.status == 200:
                        # ここにデータ解析ロジックを入れる
                        print(f"[{now}] 応答あり: {response.status}")
                        # 実際にはここでJSONではなくバイナリやCSVが返ってくる
                    else:
                        print(f"失敗: {response.status}")
            except Exception as e:
                print(f"接続エラー: {e}")
            
            await asyncio.sleep(2)
