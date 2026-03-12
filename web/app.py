from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    configurations = []
    if request.method == "POST":
        kwargs = {
            "kraken_quick": bool(request.form.get("kraken-quick")),
            "kraken_confidence": float(request.form.get("kraken-confidence")),
            "kraken_threads": int(request.form.get("kraken-threads"))
        }
        configurations = [f"{key}: {value}" for key, value in kwargs.items()]
    return render_template('index.html', title="Pipeline", configurations=configurations)


@app.route("/about")
def about():
    return render_template('about.html', title="About")


@app.route("/how-to")
def usage():
    return render_template('usage.html', title="How to use")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
