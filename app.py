from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hockey")
def hockey():
    return render_template("hockey.html")

@app.route("/football")
def football():
    return render_template("football.html")

@app.route("/compare")
def compare():
    return render_template("compare.html")

if __name__ == "__main__":
    app.run(debug=True)
