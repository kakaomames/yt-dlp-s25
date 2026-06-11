import json

def get_best_thumbnail(thumbnails):
    """ サムネイルリストから一番最後（高画質）のリンクを取得! """
    if isinstance(thumbnails, list) and len(thumbnails) > 0:
        return thumbnails[-1].get("url")
    return None

import json
import re

def logtodata(file_path='log.txt'):
    """ JSONファイルがゴミデータを含んでいても、最初のJSONオブジェクトを抽出する """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. もしファイル全体がリストならそのまま、そうでなければ最初のJSONを探す
        # 正規表現で最初の { から最後まで、あるいは複数ある場合は最初の1つだけを狙う
        # ここでは一番安定する json.decoder を利用する
        decoder = json.JSONDecoder()
        data, index = decoder.raw_decode(content.strip())
        
        # data に最初のJSONが入る。index は読み終わった位置。
        # data がリストならそのまま、dictならリスト化
        items = data if isinstance(data, list) else [data]
        
        results = []
        for item in items:
            # ... (既存の抽出ロジックはそのまま) ...
            all_formats = item.get("formats") or []
            manifest_urls = [
                f.get("url") for f in all_formats 
                if f.get("url") and "manifest.googlevideo.com" in f.get("url")
            ]
            
            extracted = {
                "id": item.get("id"),
                "title": item.get("fulltitle"),
                "channel": item.get("channel"),
                "channel_id": item.get("uploader_id"),
                "channel_url": item.get("uploader_url"),
                "follower_count": item.get("channel_follower_count"),
                "upload_date": item.get("upload_date"),
                "duration": item.get("duration_string"),
                "view_count": item.get("view_count"),
                "like_count": item.get("like_count"),
                "comment_count": item.get("comment_count"),
                "tags": item.get("tags"),
                "description": item.get("description"),
                "thumbnail_url": get_best_thumbnail(item.get("thumbnails")),
                "manifest_urls": manifest_urls
            }
            results.append(extracted)
            
        return results[0] if len(results) == 1 else results

    except json.JSONDecodeError as e:
        return {"error": f"探検隊エラー: JSONの形式が崩れています。ゴミデータが含まれていないか確認してください。詳細: {str(e)}"}
    except Exception as e:
        return {"error": f"探検隊エラー: {str(e)}"}


def logtodattyyyu7a(file_path='log.txt'):
    """ JSONファイルを読み込み、指定された項目を抽出する """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = data if isinstance(data, list) else [data]
        results = []
        
        for item in items:
            # マニフェストURLの抽出
            all_formats = item.get("formats") or []
            manifest_urls = [
                f.get("url") for f in all_formats 
                if f.get("url") and "manifest.googlevideo.com" in f.get("url")
            ]
            
            # 必要な全データを網羅
            extracted = {
                "id": item.get("id"),
                "title": item.get("fulltitle"),
                "channel": item.get("channel"),
                "channel_id": item.get("uploader_id"),  # ここで追加！
                "channel_url": item.get("uploader_url"),
                "follower_count": item.get("channel_follower_count"),
                "upload_date": item.get("upload_date"),
                "duration": item.get("duration_string"),
                "view_count": item.get("view_count"),
                "like_count": item.get("like_count"),
                "comment_count": item.get("comment_count"),
                "tags": item.get("tags"),
                "description": item.get("description"),
                "thumbnail_url": get_best_thumbnail(item.get("thumbnails")),
                "manifest_urls": manifest_urls
            }
            results.append(extracted)
            
        return results[0] if len(results) == 1 else results

    except Exception as e:
        return {"error": f"探検隊エラー: {str(e)}"}

# --- メイン実行部 ---
log = logtodata()
print(json.dumps(log, ensure_ascii=False))
