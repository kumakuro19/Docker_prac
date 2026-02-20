# HOWTO: ブラウザで .py を変換してダウンロードする

この手順書は、現在の実装（MVP）に合わせた実行方法です。

## 0. ゴール

- Docker 上で変換ツールを起動する
- ブラウザで `.py` を選択して変換を開始する
- 生成 ZIP をダウンロードする

## 1. 事前確認

```bash
docker --version
docker compose version
```

## 2. プロジェクトへ移動

```bash
cd /home/pi/Desktop/docker1
```

## 3. 起動

```bash
docker compose up --build
```

## 4. ブラウザ操作

1. `http://localhost:5000` を開く
2. `Pythonファイル (.py)` で変換対象ファイルを選択
3. `変換開始` を押す
4. `*_converted.zip` がダウンロードされる

## 5. ZIP の中身

- `src/<元ファイル名>.py`
- `run.sh` (Raspberry Pi / Linux 実行用)
- `run.bat` (Windows 実行用)
- `build_exe.bat` (Windows で EXE 生成)
- `README_CONVERTED.md`

## 6. 停止

```bash
docker compose down
```

## 7. よくあるエラー

- `.py ファイルのみ対応しています。`
  - `.py` 以外を選択しています
- `空ファイルは変換できません。`
  - 0バイトファイルです
- ダウンロードされない
  - ブラウザのダウンロード制限やポップアップ制御を確認してください

## 8. 補足

- 現状は「実行パッケージを生成する」機能です。
- 本格的な自動UI変換は次フェーズで仕様化して実装します。
