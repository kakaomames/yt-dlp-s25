import subprocess
import time

WAIT_TIME = 10  # 1時間

def main():
    print("\n[LOG] syp.sh 実行")
    subprocess.run(["bash", "syp.sh"])

def wait_meter(seconds):
    for i in range(seconds):
        percent = int((i + 1) / seconds * 100)

        bar_length = 30
        filled = int(percent / 100 * bar_length)

        bar = "■" * filled + "□" * (bar_length - filled)

        print(f"\r[{bar}] {percent}%", end="")
        time.sleep(1)

    print()

if __name__ == "__main__":
    while True:
        main()
        wait_meter(WAIT_TIME)