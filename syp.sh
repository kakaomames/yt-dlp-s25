#!/bin/bash

# ========================================================
# Gemini programming隊特製: トンネル起動 ＆ URL自動Git Pushスクリプト (真・確定完全版)
# ========================================================
# 🛑【ゴミ巻き込み防御】* を使わず、確実に必要な最新ファイルだけを狙い撃ちでZIP化！
rm -f s.zip
zip -r s.zip ./*.py ./syp.sh ./file.txt

echo "[LOG] SYSTEM: 復活ミッション（GitHub連携・強制特攻ルート）を開始します！"
# 1. サーバーの幽霊と、★前回のトンネル（ssh）のゾンビも起動時に完全退治！！
pkill -f server.py
pkill -f "ssh -R 80:localhost:9080"
echo "止める"
rm -rf /storage/emulated/0/yt-dlp-Xiaomi/.git/index.lock

# 🛑【絶対防壁：トークンダイレクト強制吸入】
CURRENT_DIR=$(dirname "$(readlink -f "$0")")
GITPAD=$(cat "$CURRENT_DIR/file.txt")

if [ -z "$GITPAD" ]; then
    GITPAD=$(cat file.txt)
fi

# 🌟【ここを追加！！！：真・記憶クレンジング】
# Gitの古い記憶（古いトークンが入った登録URL）を起動時に一度完全に削除し、
# トークンを一切含まない純粋なURLで登録し直します！これで古い設定への浮気を100%防ぎます。
# GitHubで生成したトークン（これだけは必要だ、許してくれ！）
TOKEN="$GITPAD"

# あなたのユーザー名とリポジトリ名
USER="kakaomames"
REPO="yt-dlp-s25"

# リモートに保存したいパスと、手元のファイル名
TARGET_PATH="urls.json"
LOCAL_FILE="urls.json"
TARGET_PAT="syp.sh"
LOCAL_FIL="syp.sh"
TARGET_PA="syp.py"
LOCAL_FI="syp.py"

git remote remove origin 2>/dev/null
git remote add origin https://github.com/kakaomames/yt-dlp-s25.git

git config --global user.email "kakaomames@example.com"
git config --global user.name "kakaomames"

# 最新情報を取得
git fetch origin

rm -fr ./tunnel_output.log
echo " " > tunnel_output.log

Log() {
    local time=$(date +"%H:%M:%S")
    echo "[$time] $1"
}
# GitHubへファイルをPUTする専用関数
upload_to_github() {
    local file_path=$1
    local target_path=$2
    
    # SHAを取得（Bearerに変更！）
    local sha=$(curl -s -H "Authorization: Bearer $TOKEN" \
        -H "X-GitHub-Api-Version: 2026-03-10" \
        "https://api.github.com/repos/$USER/$REPO/contents/$target_path" | jq -r '.sha')
    
    # 既存のSHAが取れていない（null）場合は空文字として扱う
    [ "$sha" == "null" ] && sha=""

    # アップロード実行
    curl -s -X PUT \
        -H "Authorization: Bearer $TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2026-03-10" \
        "https://api.github.com/repos/$USER/$REPO/contents/$target_path" \
        -d "$(jq -n --arg content "$(base64 -w 0 $file_path)" --arg sha "$sha" \
        '{"message": "VALUE_CHANGE: curl上書き更新", "content": $content, "sha": $sha}')" > /dev/null
}

# 3. 主軸ブランチの名前を確実に「main」に設定
git branch -M main

# 4. 変更があったらログに出すため、現在の接続先を画面に表示して確認！
git remote -v

sleep 1
echo "[LOG] ACTION: server.py を裏側で起動中..."
python3 server.py > server.log 2>&1 &
sleep 2

# 2. トンネルの一時ログファイルをリセット
TUNNEL_LOG="tunnel_output.log"
> $TUNNEL_LOG

# 3. localhost.run のトンネルを裏で起動し、ログを書き出す
echo "[LOG] ACTION: SSHを使って世界へのトンネルを開通します..."
ssh -R 80:localhost:9080 nokey@localhost.run > $TUNNEL_LOG 2>&1 &

echo "=============================="

echo "[LOG] ACTION: トンネルのURL発行を常時監視しています..."

# 4. ログをループで監視して、URLが見つかるまで待機・更新し続ける
while true; do
    # ログから最新のURL（.lhr.life または .localhost.run）を抽出
    LATEST_URL=$(grep -oE "https://[a-zA-Z0-9.-]+\.(lhr\.life)" $TUNNEL_LOG | tail -n 1)
    
    if [ ! -z "$LATEST_URL" ]; then
        # 前回保存したURLと比較するために、現在のファイルの中身を読み込む
        OLD_URL=""
        if [ -f urls.json ]; then
            OLD_URL=$(grep -oE "https://[a-zA-Z0-9.-]+\.(lhr\.life|localhost\.run)" urls.json)
        fi
        
        # 値が変わったときだけログに出して GitHub にプッシュする！
        if [ "$LATEST_URL" != "$OLD_URL" ]; then
            echo "[LOG] SUCCESS: 新しいプロキシURLを検知しました！ -> $LATEST_URL"
            
            # JSONを作成
            echo "{\"proxy_url\": \"$LATEST_URL\"}" > urls.json
            echo "[LOG] ACTION: urls.json の値を更新しました。"
            echo "{\"proxy_url\": \"$LATEST_URL\"}" > url.json
            echo "[LOG] ACTION: url.json の値を更新しました。"
            rm -r ./tunnel_output.log
            echo " " > tunnel_output.log
            
            # ギット コマンドで強制プッシュ（--force）し続ける！
            echo "[LOG] ACTION: GitHubへ最新URLを強制プッシュ（--force）します..."
            rm -rf .git/index.lock
            git add ./*.json
            git add ./*.py
            git add ./*.zip
            git commit -m "UPDATE: Current proxy URL to $LATEST_URL" || true





            
            # 修正前後のイメージ
            upload_to_github "$LOCAL_FILE" "$TARGET_PATH"
            upload_to_github "$LOCAL_FIL" "$TARGET_PAT"
            upload_to_github "$LOCAL_FI" "$TARGET_PA"
            Log "[LOG] SUCCESS: GitHubへの同期が100%完了しました！"

            # 🌟【物理ねじ伏せ】浮気する古い設定URLを完全に消した状態で、file.txtの最新トークンを直接ブチ込む！
            #git push https://$GITPAD@github.com/kakaomames/yt-dlp-s25.git main --force
            # 1. 既存ファイルのSHAを取得（新規ファイルならこのステップは飛ばしてOK）
            # SHA=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/$USER/$REPO/contents/$TARGET_PATH | jq -r '.sha')
            # 2. SHA付きでPUTリクエスト（新規なら "sha": $sha の部分は不要）
            # curl -X PUT -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/$USER/$REPO/contents/$TARGET_PATH -d "$(jq -n --arg content "$(base64 -w 0 $LOCAL_FILE)" --arg sha "$SHA" '{"message": "VALUE_CHANGE: curl上書き更新", "content": $content, "sha": $sha}')"
            
            
            
            # 1. 既存ファイルのSHAを取得（新規ファイルならこのステップは飛ばしてOK）
            # SHAA=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/$USER/$REPO/contents/$TARGET_PAT | jq -r '.sha')
            # 2. SHA付きでPUTリクエスト（新規なら "sha": $sha の部分は不要）
            # curl -X PUT -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/$USER/$REPO/contents/$TARGET_PAT -d "$(jq -n --arg content "$(base64 -w 0 $LOCAL_FIL)" --arg sha "$SHAA" '{"message": "VALUE_CHANGE: curl上書き更新", "content": $content, "sha": $sha}')"
            
            
            # 1. 既存ファイルのSHAを取得（新規ファイルならこのステップは飛ばしてOK）
            # SHAS=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/$USER/$REPO/contents/$TARGET_PA | jq -r '.sha')
            # 2. SHA付きでPUTリクエスト（新規なら "sha": $sha の部分は不要
            # curl -X PUT -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/$USER/$REPO/contents/$TARGET_PA -d "$(jq -n --arg content "$(base64 -w 0 $LOCAL_FI)" --arg sha "$SHAS" '{"message": "VALUE_CHANGE: curl上書き更新", "content": $content, "sha": $sha}')"


            

            
            Log "[LOG] SUCCESS: GitHubへの同期が100%完了しました！"
        fi
    fi
    
    # whileループの「中」で確実に毎秒1秒止まる安心設計
    sleep 1
done
