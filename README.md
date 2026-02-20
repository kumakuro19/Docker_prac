# Docker Flask Practice

Docker コンテナで `Python(Flask) + HTML/JS` を動かす、学習用の最小プロジェクトです。

## 目的

- Docker を使ったローカル開発の基本を学ぶ
- Python(Flask) で API を作る流れを体験する
- HTML/JS から API を呼び出すフロント連携を理解する

## できること

- `GET /` で画面を表示
- 画面のボタン押下で `GET /api/hello?name=...` を実行
- API の JSON レスポンスを画面に表示

## プロジェクト構成

```text
.
├── app
│   ├── main.py                 # Flaskアプリ本体（画面配信 + API）
│   ├── templates
│   │   └── index.html          # 画面HTML
│   └── static
│       ├── script.js           # API呼び出し処理
│       └── style.css           # 画面スタイル
├── Dockerfile                  # Python実行イメージ
├── docker-compose.yml          # コンテナ起動設定
├── requirements.txt            # Python依存関係
└── .dockerignore               # Dockerビルド除外設定
```

## 前提環境

- Docker
- Docker Compose (`docker compose` コマンドが使えること)

## 操作方法

### 1. 起動

```bash
cd /home/pi/Desktop/docker1
docker compose up --build
```

初回はイメージ作成のため少し時間がかかります。

### 2. ブラウザで確認

- `http://localhost:5000` を開く
- 名前を入力して `送信` ボタンを押す
- 画面下に `Hello, <入力した名前>!` が表示される

### 3. 停止

```bash
docker compose down
```

### 4. ログ確認（必要時）

```bash
docker compose logs -f
```

## 開発メモ

- `docker-compose.yml` で `./app:/app/app` をマウントしているため、`app` 配下の変更はコンテナに即反映されます。
- `main.py` は `debug=True` なので、Pythonコード変更時に自動リロードされます。

## API 仕様（現状）

### `GET /api/hello`

- Query:
  - `name` (任意)
- Response (JSON):

```json
{
  "message": "Hello, Taro!"
}
```

`name` が未指定または空の場合は `world` が使われます。
