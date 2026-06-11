import subprocess
import time
import signal

RUN_TIME = 450  # 1時間

while True:
    print("\n[LOG] syp.sh 起動")

    proc = subprocess.Popen(["bash", "syp.sh"])

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
            print("\n[LOG] syp.sh が終了しました")
            break

        time.sleep(1)

    else:
        # 1時間経過
        print("\n[LOG] 1時間経過、停止します")
        proc.send_signal(signal.SIGINT)

        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("[LOG] 停止しないので強制終了")
            proc.kill()

    print("[LOG] 再起動します")