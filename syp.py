import subprocess
import time

def main():
    print("[LOG] syp.sh 実行")
    subprocess.run(["bash", "syp.sh"])

if __name__ == '__main__':
    print("[LOG] SYSTEM: ========================================================")
    print("[LOG] SYSTEM: ========================================================")

    while True:
        main()
        time.sleep(10)  # 1時間待機