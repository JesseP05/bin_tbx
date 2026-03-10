from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def index(title="Pipeline"):
    return render_template('index.html')


@app.route("/about")
def about(title="About"):
    return render_template('about.html')


@app.route("/how-to")
def usage(title="Usage Instructions"):
    return render_template('usage.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
