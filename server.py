import os
import subprocess
import json
import glob
import uuid
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# 一時ファイルを格納するディレクトリ（なければ作成）-
TMP_DIR = "download_tasks"
os.makedirs(TMP_DIR, exist_ok=True)

# ユーティリティ関数: 各タスクのファイルパスを生成
def get_task_paths(task_id):
    # 安全のため、渡されたUUID文字列から余計なパス記号を排除
    safe_id = "".join(c for c in task_id if c.isalnum() or c == '-')
    video_path = os.path.join(TMP_DIR, f"{safe_id}.mp4")
    log_path = os.path.join(TMP_DIR, f"{safe_id}.log")
    return video_path, log_path

# ========================================================
# ⚔️ ルート1: /json （情報高速返送モード）
# ========================================================

@app.route('/json', methods=['GET'])
def get_video_json():
    # パラメータを 'u' に対応させたぞ！
    video_url = request.args.get('url')
    if not video_url:
        print("[LOG] ERROR [/json]: URLが指定されていません。")
        return jsonify({"error": "URL is required"}), 400
        
    print(f"[LOG] ACTION [/json]: 情報解析リクエストを受信。 URL: {video_url}")
    
    try:
        # 1. yt-dlp で log.txt を生成
        print("[LOG] ACTION [/json]: yt-dlp プロセスを起動します。")
        with open("log.txt", "w") as f_log:
            subprocess.run(["yt-dlp", "-j", video_url], stdout=f_log, check=True)
        
        # 2. log.py を実行して log2.json を生成（log.py側でファイル保存している前提）
        print("[LOG] ACTION [/json]: log.py を起動します。")
        with open("log2.json", "w") as f_log:
            subprocess.run(["python", "log.py"], stdout=f_log, check=True)
        print("[LOG] SUCCESS [/json]: 解析完了。log2.json を送信します。")
        with open("log2.json", "r", encoding="utf-8") as f:
            result_data = json.load(f)
        subprocess.run(["git", "add", "./*.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Saved video config to log2.json via Termux on Galaxy S25 & Galaxy S25でTermux経由でlog2.jsonに保存されたビデオ情報のアップ"], check=True)
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        
            
        return jsonify(result_data), 200
        
    except Exception as e:
        print(f"[LOG] ERROR [/json]: 処理失敗。詳細: {str(e)}")
        return jsonify({"error": "process failed", "details": str(e)}), 500




@app.route('/json2', methods=['GET'])
def get_video_json_2():
    video_url = request.args.get('url')
    if not video_url:
        print("[LOG] ERROR [/json]: URLが指定されていません。")
        return jsonify({"error": "URL is required"}), 400
        
    print(f"[LOG] ACTION [/json]: 情報解析リクエストを受信。 URL: {video_url}")
    command = ["yt-dlp", "-j", video_url, ">","log.txt"]
    cmd2 = ["python","log.py",">" ,"log2.txt"]
    
    try:
        print("[LOG] ACTION [/json]: yt-dlp プロセスを起動します。")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True)
        print("[LOG] SUCCESS [/json]: 解析完了。")
        # 隊員の教えを厳守：バックスラッシュを使用した記号などはそのままにしてパース
        video_data = json.loads(result.stdout)
        return jsonify(video_data), 200
    except subprocess.CalledProcessError as e:
        print(f"[LOG] ERROR [/json]: yt-dlp 実行失敗。詳細: {e.stderr}")
        return jsonify({"error": "yt-dlp failed", "details": e.stderr}), 500


# ========================================================
# ⚔️ ルート2: /video （タスクID発行 ＆ ログ中継モード）
# ========================================================
@app.route('/video', methods=['GET'])
def manage_video_task():
    video_url = request.args.get('url')
    task_id = request.args.get('id')
    
    # 🌟 パターンA: 新規ダウンロードリクエスト（urlがある場合）
    if video_url:
        # 新しい一意のUUID（タスクID）を発行！
        new_id = str(uuid.uuid4())
        video_path, log_path = get_task_paths(new_id)
        
        print(f"[LOG] ACTION [/video]: 新規ジョブを受信。タスクID [ {new_id} ] を発番しました。 URL: {video_url}")
        
        # ログファイルを初期化
        with open(log_path, "w") as f:
            f.write(f"[LOG] SYSTEM: タスク {new_id} のバックグラウンドジョブを開始します...\n")
            
        # タスクIDをファイル名に含めてバックグラウンドで yt-dlp + ffmpeg を実行！
        # ファイル名がyt-dlpの自動拡張子生成でブレないように指定する
        # --no-part でダウンロード中に .part を作らせず、直接名前を固定する！
        # command = (
        #     f"yt-dlp -f 'bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]' --no-part -o '{video_path}' '{video_url}' >> '{log_path}' 2>&1 && "
        #     f"ffmpeg -y -i '{video_path}' -vcodec libx264 -crf 23 -acodec aac '{video_path}.final.mp4' >> '{log_path}' 2>&1 && "
        #     f"mv '{video_path}.final.mp4' '{video_path}' && "
        #     f"rm -f '{video_path}.tmp*'"
        # )
        command = (
            f"echo '[LOG] STEP1: yt-dlp ダウンロード開始...' >> '{log_path}' && "
            f"yt-dlp -f 'bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]' -o '{video_path}' '{video_url}' --embed-thumbnail -S vcodec:h264,res:720,acodec:m4a >> '{log_path}' 2>&1 && "
            f"echo '[LOG] STEP2: yt-dlp 完了。ffmpeg 変換開始...' >> '{log_path}' && "
            # f"ffmpeg -y -i '{video_path}' -vcodec libx264 -preset ultrafast -crf 25 -acodec aac -b:a 128128k '{video_path}.final.mp4' >> '{log_path}' 2>&1 && "
            # f"mv '{video_path}.final.mp4' '{video_path}' && "
            f"echo '[LOG] STEP3: すべてのプロセスが完了しました。' >> '{log_path}'"
        )


        subprocess.Popen(command, shell=True)
        print(f"[LOG] SUCCESS [/video]: タスク {new_id} をバックグラウンドに投入しました。")
        # Vercelには即座に「新しく発行したタスクID」を返す（タイムアウト回避！）
        
        return jsonify({"status": "started", "task_id": new_id}), 200

        
        


    # 🌟 パターンB: 進捗確認リクエスト（idが指定されている場合）
    # 🌟 パターンB: 進捗確認リクエスト
    if task_id:
        video_path, log_path = get_task_paths(task_id)
        
        if not os.path.exists(log_path):
            return jsonify({"status": "not_found", "log": "Task not found."}), 404
            
        with open(log_path, "r") as f:
            log_content = f.read()
            
        # ここで一括判定！
        if "STEP3: すべてのプロセスが完了しました。" in log_content:
            status = "complete"
        elif "STEP2: yt-dlp 完了。ffmpeg 変換開始..." in log_content:
            status = "processing"
        else:
            status = "downloading"
            
        return jsonify({"status": status, "task_id": task_id, "log": log_content}), 200


    # urlもidもない場合はエラー
    return jsonify({"error": "Either 'url' or 'id' parameter is required"}), 400


# ========================================================
# ⚔️ ルート3: /watch （指定したタスクIDの動画ストリーミング）
# ========================================================
@app.route('/watch', methods=['GET'])
def watch_video():
    task_id = request.args.get('id')
    if not task_id:
        print("[LOG] ERROR [/watch]: タスクIDが指定されていません。")
        return jsonify({"error": "Task 'id' is required"}), 400
        
    video_path, _ = get_task_paths(task_id)
    print(f"[LOG] ACTION [/watch]: タスク [ {task_id} ] の動画配信リクエストを受信。")
    
    if os.path.exists(video_path):
        print(f"[LOG] SUCCESS [/watch]: タスク [ {task_id} ] の動画実体を発見！ストリーミングを開始します。")
        return send_file(video_path, mimetype="video/mp4")
    else:
        print(f"[LOG] ERROR [/watch]: タスク [ {task_id} ] の動画ファイルが未完成か、既に削除されています。")
        return jsonify({"error": "Video file not found. It might still be downloading or removed."}), 404


# ========================================================
# ⚔️ ルート4: /remove （男気全削除モード：すべてのファイルを完全無条件爆破）
# ========================================================
@app.route('/remove', methods=['GET'])
def remove_all_files():
    print("[LOG] ACTION [/remove]: クリーンアップ命令を受信！タスクIDに関わらず、すべての動画データを焦土と化します！")
    
    deleted_files = []
    
    # download_tasks ディレクトリ内のすべてのファイルを列挙して削除
    target_files = glob.glob(os.path.join(TMP_DIR, "*"))
    for fpath in target_files:
        try:
            os.remove(fpath)
            deleted_files.append(fpath)
        except Exception as e:
            print(f"[LOG] WARNING [/remove]: ファイル {fpath} の削除に失敗: {str(e)}")
            
    print(f"[LOG] SUCCESS [/remove]: 爆破完了！ 削除したファイル総数: {len(deleted_files)} 件")
    return jsonify({
        "success": True, 
        "message": "All task videos and logs have been completely and unconditionally wiped out.", 
        "deleted_count": len(deleted_files),
        "deleted_list": deleted_files
    }), 200


if __name__ == '__main__':
    print("[LOG] SYSTEM: ========================================================")
    print("[LOG] SYSTEM: Gemini programming隊特製 『UUIDタスク管理＆無条件爆破』プロキシ 起動")
    print("[LOG] SYSTEM: 🗺️  /json             -> 動画情報取得")
    print("[LOG] SYSTEM: 🗺️  /video?url=...   -> 新規タスクID発行＆DL開始")
    print("[LOG] SYSTEM: 🗺️  /video?id=UUID   -> 指定タスクのログ中継 (ポーリング先)")
    print("[LOG] SYSTEM: 🗺️  /watch?id=UUID   -> 指定タスクの動画ストリーミング")
    print("[LOG] SYSTEM: 🗺️  /remove           -> 全タスクデータの完全無条件爆破")
    print("[LOG] SYSTEM: ========================================================")
    app.run(host='0.0.0.0', port=9080)
