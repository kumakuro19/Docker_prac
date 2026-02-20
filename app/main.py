import io
import os
import posixpath
import tempfile
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)
MAX_SOURCE_BYTES = 1024 * 1024
MAX_ARCHIVE_BYTES = 20 * 1024 * 1024


@app.get("/")
def index():
    return render_template("index.html")


def _convert_github_url_to_raw(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URLは http/https のみ対応しています。")

    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if host == "raw.githubusercontent.com":
        return url
    if host != "github.com":
        raise ValueError("GitHub URLのみ対応しています。")

    parts = [p for p in path.split("/") if p]
    if len(parts) < 5 or parts[2] != "blob":
        raise ValueError("GitHubの .py ファイルURL（.../blob/...）を指定してください。")
    if not parts[-1].lower().endswith(".py"):
        raise ValueError(".py ファイルのURLを指定してください。")

    user, repo, _, branch = parts[:4]
    file_path = "/".join(parts[4:])
    return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"


def _read_source_from_url(github_url: str):
    raw_url = _convert_github_url_to_raw(github_url)
    filename = Path(urlparse(raw_url).path).name
    try:
        with urlopen(raw_url, timeout=15) as response:
            source = response.read(MAX_SOURCE_BYTES + 1)
    except HTTPError as exc:
        raise ValueError(f"URL取得に失敗しました: HTTP {exc.code}") from exc
    except URLError as exc:
        raise ValueError("URL取得に失敗しました。URLを確認してください。") from exc

    if len(source) > MAX_SOURCE_BYTES:
        raise ValueError("ファイルサイズ上限(1MB)を超えています。")
    if not source:
        raise ValueError("URL先のファイルが空です。")
    return filename, source


def _zip_write_text(zf: zipfile.ZipFile, path: str, content: str, executable: bool = False):
    info = zipfile.ZipInfo(path)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = 0o755 if executable else 0o644
    info.external_attr = mode << 16
    zf.writestr(info, content)


def _safe_member_name(name: str) -> str:
    normalized = name.replace("\\", "/").strip("/")
    cleaned = posixpath.normpath(normalized)
    if cleaned in {"", "."}:
        return ""
    if cleaned.startswith("../") or cleaned == ".." or cleaned.startswith("/"):
        return ""
    return cleaned


def _infer_entry_from_project(entries: list[str]) -> str:
    py_files = [p for p in entries if p.lower().endswith(".py")]
    if not py_files:
        raise ValueError("アーカイブ内に .py ファイルが見つかりません。")
    if len(py_files) == 1:
        return py_files[0]
    if "main.py" in py_files:
        return "main.py"
    if "src/main.py" in py_files:
        return "src/main.py"
    raise ValueError(
        "起動対象の .py を特定できません。main_script に例: src/main.py のように指定してください。"
    )


def _read_files_from_zip(payload: bytes):
    try:
        source_zip = zipfile.ZipFile(io.BytesIO(payload), "r")
    except zipfile.BadZipFile as exc:
        raise ValueError("ZIPファイルの形式が不正です。") from exc

    files: list[tuple[str, bytes]] = []
    with source_zip:
        for member in source_zip.infolist():
            if member.is_dir():
                continue
            safe_name = _safe_member_name(member.filename)
            if not safe_name:
                continue
            files.append((safe_name, source_zip.read(member)))
    return files


def _read_files_from_7z(payload: bytes):
    try:
        import py7zr
    except ImportError as exc:
        raise ValueError(".7z 対応ライブラリ(py7zr)が未インストールです。") from exc

    files: list[tuple[str, bytes]] = []
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with py7zr.SevenZipFile(io.BytesIO(payload), mode="r") as source_7z:
                source_7z.extractall(path=tmp_dir)

            for root, _, filenames in os.walk(tmp_dir):
                for filename in filenames:
                    full_path = Path(root) / filename
                    rel_path = full_path.relative_to(tmp_dir).as_posix()
                    safe_name = _safe_member_name(rel_path)
                    if not safe_name:
                        continue
                    files.append((safe_name, full_path.read_bytes()))
    except Exception as exc:
        raise ValueError("7zファイルの展開に失敗しました。") from exc

    return files


def _load_project_from_archive(project_zip, main_script: str):
    if not project_zip or not project_zip.filename:
        raise ValueError("アーカイブファイルを選択してください。")

    archive_name = Path(project_zip.filename).name
    suffix = Path(archive_name).suffix.lower()
    if suffix not in {".zip", ".7z"}:
        raise ValueError("プロジェクトは .zip または .7z 形式でアップロードしてください。")

    payload = project_zip.read(MAX_ARCHIVE_BYTES + 1)
    if len(payload) > MAX_ARCHIVE_BYTES:
        raise ValueError("アーカイブサイズ上限(20MB)を超えています。")
    if not payload:
        raise ValueError("空のアーカイブは変換できません。")

    if suffix == ".zip":
        files = _read_files_from_zip(payload)
    else:
        files = _read_files_from_7z(payload)

    if not files:
        raise ValueError("アーカイブ内に有効なファイルが見つかりません。")

    all_paths = [p for p, _ in files]
    entry = main_script.strip().replace("\\", "/").strip("/") if main_script else ""
    if entry:
        if entry not in all_paths:
            raise ValueError(f"main_script がアーカイブ内に見つかりません: {entry}")
        if not entry.lower().endswith(".py"):
            raise ValueError("main_script には .py ファイルを指定してください。")
    else:
        entry = _infer_entry_from_project(all_paths)

    base_name = Path(archive_name).stem
    return base_name, files, entry


def _make_output_zip(base_name: str, files: list[tuple[str, bytes]], entry: str):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path, content in files:
            zf.writestr(f"{base_name}/project/{rel_path}", content)

        entry_unix = entry
        entry_win = entry.replace("/", "\\")
        _zip_write_text(
            zf,
            f"{base_name}/run.sh",
            f"""#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/project"
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 が見つかりません。先に Python3 をインストールしてください。"
  exit 1
fi
python3 "{entry_unix}" "$@"
""",
            executable=True,
        )
        _zip_write_text(
            zf,
            f"{base_name}/run.bat",
            f"""@echo off
setlocal
cd /d %~dp0\\project
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 "{entry_win}" %*
  exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python "{entry_win}" %*
  exit /b %ERRORLEVEL%
)

echo Python launcher (py) または python が見つかりません。
exit /b 1
""",
        )
        _zip_write_text(
            zf,
            f"{base_name}/build_exe.bat",
            f"""@echo off
setlocal
cd /d %~dp0\\project
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 -m pip install pyinstaller
  py -3 -m PyInstaller --onefile "{entry_win}" --name "{base_name}"
) else (
  python -m pip install pyinstaller
  python -m PyInstaller --onefile "{entry_win}" --name "{base_name}"
)
echo Build finished. Output: project\\dist\\{base_name}.exe
""",
        )
        _zip_write_text(
            zf,
            f"{base_name}/README_CONVERTED.md",
            f"""# Converted Package: {base_name}

Entry script: `{entry_unix}`

## Raspberry Pi (Linux)
```bash
bash run.sh
```

## Windows
- Run script directly:
```bat
run.bat
```
- Build EXE:
```bat
build_exe.bat
```

## Note
- `project/` 配下に元ファイル構成を保持しています。
- 依存ライブラリがある場合は、事前に環境へインストールしてください。
""",
        )

    zip_buffer.seek(0)
    return zip_buffer


@app.post("/api/convert")
def convert():
    py_file = request.files.get("py_file")
    project_zip = request.files.get("project_zip")
    github_url = request.form.get("github_url", "").strip()
    main_script = request.form.get("main_script", "").strip()

    try:
        if project_zip and project_zip.filename:
            base_name, files, entry = _load_project_from_archive(project_zip, main_script)
        elif py_file and py_file.filename:
            filename = Path(py_file.filename).name
            if not filename.lower().endswith(".py"):
                return jsonify({"error": ".py ファイルのみ対応しています。"}), 400

            source = py_file.read(MAX_SOURCE_BYTES + 1)
            if len(source) > MAX_SOURCE_BYTES:
                return jsonify({"error": "ファイルサイズ上限(1MB)を超えています。"}), 400
            if not source:
                return jsonify({"error": "空ファイルは変換できません。"}), 400

            base_name = Path(filename).stem
            files = [(f"src/{filename}", source)]
            entry = f"src/{filename}"
        elif github_url:
            filename, source = _read_source_from_url(github_url)
            base_name = Path(filename).stem
            files = [(f"src/{filename}", source)]
            entry = f"src/{filename}"
        else:
            return (
                jsonify(
                    {
                        "error": (
                            "project_zip / py_file / github_url のいずれかを指定してください。"
                        )
                    }
                ),
                400,
            )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    zip_buffer = _make_output_zip(base_name, files, entry)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{base_name}_converted.zip",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
