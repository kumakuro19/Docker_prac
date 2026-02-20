# HOWTO: フォルダ依存ありPythonを変換して動かす

## 0. ゴール

- Docker 上で変換ツールを起動
- ZIPまたは `.py` を変換
- 出力ZIPを別ラズパイ/Windowsで実行

## 1. 起動

```bash
cd /home/pi/Desktop/docker1
docker compose up --build
```

## 2. ブラウザ操作

1. `http://localhost:5000` を開く
2. 次のどれかを指定
   - `プロジェクトZIP（推奨）`
   - `Pythonファイル (.py)`
   - `GitHub .py URL`
3. ZIPを使う場合、必要に応じて `main_script` を入力（例: `src/main.py`）
4. `変換開始`
5. `*_converted.zip` をダウンロード

## 3. ZIP入力の作り方（重要）

- プロジェクトのルートフォルダごとZIP化
- 相対パスで参照するデータファイルや設定ファイルも含める

例:

```text
my_app/
├── src/
│   └── main.py
├── data/
│   └── config.json
└── requirements.txt
```

この場合、`main_script` は `src/main.py`

## 4. 変換後の実行

### Raspberry Pi / Linux

```bash
cd <展開先>/<変換名>
bash run.sh
```

### Windows

```bat
cd <展開先>\<変換名>
run.bat
```

### Windows exe生成

```bat
build_exe.bat
```

## 5. よくあるエラー

- `main_script がZIP内に見つかりません`
  - パス指定が違います（`/` 区切りで入力）
- `起動対象の .py を特定できません`
  - `.py` が複数あります。`main_script` を指定してください
- `ZIP内に .py ファイルが見つかりません`
  - ZIP内容を確認してください

## 6. 補足

- 入力優先順位は `project_zip > py_file > github_url`
- 現状は実行パッケージ生成まで。自動UI変換は次フェーズです。
