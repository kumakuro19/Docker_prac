# Docker Flask Practice

Docker コンテナで `Python(Flask) + HTML/JS` を動かす、学習用の最小プロジェクトです。

## 目的

- Docker を使ったローカル開発の基本を学ぶ
- Python(Flask) で API を作る流れを体験する
- ブラウザ操作で `.py` ファイルを変換し、生成物をダウンロードする

## できること（現在）

- `GET /` で変換UIを表示
- ブラウザで `.py` ファイルを選択して `変換開始`
- `POST /api/convert` で変換パッケージ（ZIP）を生成
- ZIP に以下を含めてダウンロード
  - 元の Python ファイル
  - Raspberry Pi 向け `run.sh`
  - Windows 向け `run.bat`
  - Windows で EXE 生成する `build_exe.bat`

## プロジェクト構成

```text
.
├── app
│   ├── main.py                 # Flaskアプリ本体（画面配信 + 変換API）
│   ├── templates
│   │   └── index.html          # 変換画面
│   └── static
│       ├── script.js           # アップロード/ダウンロード処理
│       └── style.css           # 画面スタイル
├── Dockerfile                  # Python実行イメージ
├── docker-compose.yml          # コンテナ起動設定
├── requirements.txt            # Python依存関係
├── .dockerignore               # Dockerビルド除外設定
└── .gitignore                  # Git除外設定
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

### 2. ブラウザで確認

- `http://localhost:5000` を開く
- `.py` ファイルを選択
- `変換開始` を押す
- 生成された `*_converted.zip` がダウンロードされる

### 3. 停止

```bash
docker compose down
```

## API 仕様（現状）

### `POST /api/convert`

- FormData:
  - `py_file` (`.py` ファイル, 必須)
- Response:
  - 成功時: ZIP ファイル
  - 失敗時: JSON エラー

## 注意

- 現状は「実行用パッケージ生成」の MVP です。
- `.py` の内容を解析して自動でブラウザUIへ完全変換する機能は未実装です。
