from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/hello")
def hello():
    name = request.args.get("name", "world").strip() or "world"
    return jsonify({"message": f"Hello, {name}!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
