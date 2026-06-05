import json

def get_best_thumbnail(thumbnails):
    """ サムネイルリストから一番最後（高画質）のリンクを取得 """
    if isinstance(thumbnails, list) and len(thumbnails) > 0:
        return thumbnails[-1].get("url")
    return None

def logtodata(file_path='log.txt'):
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
