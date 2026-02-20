# Docker Flask Practice

Docker コンテナで `Python(Flask) + HTML/JS` を動かす、学習用の最小プロジェクトです。

## 目的

- Docker を使ったローカル開発の基本を学ぶ
- Python(Flask) で API を作る流れを体験する
- ブラウザ操作で Python プロジェクトを変換し、生成物をダウンロードする

## できること（現在）

- `GET /` で変換UIを表示
- 次のどれかで変換開始
  - `project_zip`（フォルダ一式, 推奨）
  - `py_file`（単体 `.py`）
  - `github_url`（GitHub の `.py` URL）
- `POST /api/convert` で変換パッケージ（ZIP）を生成
- 出力ZIPに以下を含める
  - `project/` 配下に元の構成を保持
  - `run.sh`（Raspberry Pi/Linux実行）
  - `run.bat`（Windows実行）
  - `build_exe.bat`（Windowsでexe生成）

## 入力優先順位

`project_zip > py_file > github_url`

## フォルダ依存対応

- フォルダ依存があるアプリは、必ずプロジェクト全体を `.zip` で入力してください。
- `main_script`（例: `src/main.py`）を指定すると、そのファイルを起動対象にします。
- `main_script` 未指定時は自動判定します。
  - `.py` が1つだけならそれを採用
  - `main.py` または `src/main.py` があれば採用
  - 判定不能な場合はエラー

## 変換対象URLの形式

- 対応:
  - `https://github.com/<user>/<repo>/blob/<branch>/path/to/file.py`
  - `https://raw.githubusercontent.com/.../*.py`
- 非対応:
  - GitHub以外のURL
  - `.py` 以外の拡張子

## 操作方法

```bash
cd /home/pi/Desktop/docker1
docker compose up --build
```

- `http://localhost:5000` を開く
- `project_zip` か `.py` か GitHub URL を入力
- 必要なら `main_script` を入力
- `変換開始`

## API 仕様（現状）

### `POST /api/convert`

- FormData:
  - `project_zip` (`.zip`, 任意)
  - `main_script` (例: `src/main.py`, 任意)
  - `py_file` (`.py`, 任意)
  - `github_url` (GitHub `.py` URL, 任意)
- 条件:
  - 上記のいずれか必須
  - 優先順位: `project_zip > py_file > github_url`
- 上限:
  - `.py`: 1MB
  - `.zip`: 20MB

## 注意

- 現状は「実行パッケージ生成」の MVP です。
- 依存ライブラリがある場合、実行先で別途インストールが必要です。
- 自動UI変換（CLIからWeb画面生成）は未実装です。
