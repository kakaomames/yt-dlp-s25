import os
import subprocess
import time
import signal

# 🛑 隊員の希望通り、3600（1時間）で回す場合はここを 3600 にしてください！今は実験用に5分（300）になっています
RUN_TIME = 300  

while True:
    print("\n[LOG] syp.sh 起動")

    # 🛑【大容量インジェクション】Python側で確実に file.txt を読み込む
    git_token = ""
    if os.path.exists("file.txt"):
        with open("file.txt", "r", encoding="utf-8") as f:
            git_token = f.read().strip()

    # 現在の環境変数をコピーし、そこに確実にトークンを合流させる！
    current_env = os.environ.copy()
    current_env["GITPAD"] = git_token

    # 🛑 トークン入りの環境変数をガッチリ渡して syp.sh を起動！
    proc = subprocess.Popen(
        ["bash", "syp.sh"],
        preexec_fn=os.setsid,
        env=current_env
    )

    for i in range(RUN_TIME):
        percent = int((i + 1) / RUN_TIME * 100)

        bar_length = 20
        filled = int(bar_length * (i + 1) / RUN_TIME)

        bar = "■" * filled + "□" * (bar_length - filled)

        remain = RUN_TIME - i - 1
        mins = remain // 60
        secs = remain % 60

        print(
            f"\r[{bar}] {percent:3d}% 残り {mins:02d}:{secs:02d}",
            end="",
            flush=True
        )

        # syp.sh が先に終了したら再起動
        if proc.poll() is not None:
            print("")
            print("[LOG] VALUE_CHANGED: syp.sh が終了しました。再起動します。")
            break

        time.sleep(1)

    else:
        # 時間経過時の安全停止
        print("")
        print("[LOG] 時間経過、安全にプロセスを一度リフレッシュします。")
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGINT)
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("[LOG] 停止しないので強制終了")
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass

    print("[LOG] 再起動します")
    time.sleep(1)
