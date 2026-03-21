from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html', title="Pipeline")


@app.route("/about")
def about():
    return render_template('about.html', title="About")


@app.route("/how-to")
def usage():
    return render_template('usage.html', title="How to use")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
