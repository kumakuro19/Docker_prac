import io
import zipfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/convert")
def convert():
    uploaded = request.files.get("py_file")
    if not uploaded or not uploaded.filename:
        return jsonify({"error": "Pythonファイル(.py)を選択してください。"}), 400

    filename = Path(uploaded.filename).name
    if not filename.lower().endswith(".py"):
        return jsonify({"error": ".py ファイルのみ対応しています。"}), 400

    source = uploaded.read()
    if not source:
        return jsonify({"error": "空ファイルは変換できません。"}), 400

    base_name = Path(filename).stem
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{base_name}/src/{filename}", source)
        zf.writestr(
            f"{base_name}/run.sh",
            f"""#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 "src/{filename}" "$@"
""",
        )
        zf.writestr(
            f"{base_name}/run.bat",
            f"""@echo off
setlocal
cd /d %~dp0
python "src\\{filename}" %*
""",
        )
        zf.writestr(
            f"{base_name}/build_exe.bat",
            f"""@echo off
setlocal
cd /d %~dp0
python -m pip install pyinstaller
pyinstaller --onefile "src\\{filename}" --name "{base_name}"
echo Build finished. Output: dist\\{base_name}.exe
""",
        )
        zf.writestr(
            f"{base_name}/README_CONVERTED.md",
            f"""# Converted Package: {base_name}

## Raspberry Pi (Linux)
```bash
chmod +x run.sh
./run.sh
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
""",
        )

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{base_name}_converted.zip",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
