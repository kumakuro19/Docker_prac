# HOWTO: DockerでPython + HTML/JSアプリを動かす手順

このファイルは、はじめて Docker を触る方向けの実行手順書です。  
`README.md` よりも手順を細かく記載しています。

## 0. ゴール

- Docker コンテナ上で Flask アプリを起動する
- ブラウザから画面を開く
- ボタン操作で Python API と通信できることを確認する

## 1. 事前確認

ターミナルで次を実行して、Docker が使えるか確認します。

```bash
docker --version
docker compose version
```

どちらもバージョンが表示されれば OK です。

## 2. プロジェクトフォルダへ移動

```bash
cd /home/pi/Desktop/docker1
```

念のため、ファイルがあるか確認します。

```bash
ls
```

`Dockerfile` や `docker-compose.yml` が見えれば OK です。

## 3. コンテナを起動

```bash
docker compose up --build
```

- `--build` は、イメージを作り直して起動するオプションです。
- 初回は依存関係のインストールがあるため時間がかかります。

起動に成功すると、ログに Flask サーバーの待ち受け情報が表示されます。

## 4. ブラウザで動作確認

ブラウザで次を開きます。

- `http://localhost:5000`

画面が表示されたら以下を確認します。

1. 入力欄に名前（例: `Taro`）を入れる
2. `送信` ボタンを押す
3. `Hello, Taro!` と表示される

## 5. 停止方法

起動中ターミナルで `Ctrl + C` を押して停止します。  
その後、別途コンテナを片付ける場合は次を実行します。

```bash
docker compose down
```

## 6. よく使うコマンド

### バックグラウンド起動

```bash
docker compose up -d --build
```

### ログ確認

```bash
docker compose logs -f
```

### 停止

```bash
docker compose down
```

## 7. つまずいたときの確認ポイント

- `http://localhost:5000` が開かない  
  -> `docker compose logs -f` でエラーを確認
- `port is already allocated` が出る  
  -> 他プロセスが `5000` を使っている可能性あり。`docker-compose.yml` の左側ポートを変更
- 変更が反映されない  
  -> `docker compose down` 後に `docker compose up --build` を実行

## 8. 次の練習案

1. API を `GET` から `POST` に変更
2. 入力チェック（空文字・長すぎる文字など）を追加
3. SQLite を追加して履歴保存
4. テスト（pytest）を追加
