 1. [API とサービス] > [OAuth 同意画面]
   * 「アプリ名」と「メールアドレス」を設定して保存します。
   捕捉 : 開発中は「テストユーザー」として自分のメールアドレスを登録しておくのを忘れないように！
 2. [API とサービス] > [認証情報]
   * 「認証情報を作成」ボタンから「OAuth クライアント ID」を生成。
   * アプリの種類は「ウェブ アプリケーション」を選択。
   * これで手に入る Client ID と Client Secret が、外部からGASを叩くためのパスポートになります！
 1. 認証 URL の発行（ブラウザ用）
まず、以下の構成でURLを作り、ブラウザで開いてください。<CLIENT_ID> と <REDIRECT_URI>（http://localhost でOK）は、先ほど作成したOAuthクライアントIDのものです。

# クライアントIDなどを使って以下のURLを生成（手動でブラウザに貼り付け）
https://accounts.google.com/o/oauth2/v2/auth?
client_id=<YOUR_CLIENT_ID>&
response_type=code&
scope=https://www.googleapis.com/auth/script.projects&
redirect_uri=http://localhost&
access_type=offline&
prompt=consent

2. 認証コードのキャッチ
ブラウザで承認ボタンを押すと、リダイレクト先（http://localhost/?code=...）にURLが飛びますよね？
このURLの code= の後ろにある文字列が、今回で最も重要な「認証コード」です！コピーして確保してください

 curl コマンドで認証コードを「アクセストークン」に交換しちゃいましょう！


curl -X POST https://oauth2.googleapis.com/token \
  -d "code=<コピーしたコード>" \
  -d "client_id=<CLIENT_ID>" \
  -d "client_secret=<CLIENT_SECRET>" \
  -d "redirect_uri=http://localhost" \
  -d "grant_type=authorization_code"


このコマンドが成功すると、レスポンスとして以下のJSONが返ってきます。

{
  "access_token": "ya29.a0...",
  "refresh_token": "1//0...",
  "expires_in": 3599,
  "token_type": "Bearer"
}


注意点
 * Refresh Token: レスポンスに含まれる refresh_token は宝物です！
これが手元にあれば、アクセストークンが切れても自動で新しいトークンを取得できるので、もう一度認証画面を開く必要がなくなります
