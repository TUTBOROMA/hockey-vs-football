from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# Контекстный процессор для передачи переменной now во все шаблоны
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Главная страница
@app.route("/")
def home():
    return render_template("index.html", title="Главная")

# Страница о хоккее
@app.route("/hockey")
def hockey():
    return render_template("hockey.html", title="Хоккей")

# Страница о футболе
@app.route("/football")
def football():
    return render_template("football.html", title="Футбол")

# Страница сравнения
@app.route("/compare")
def compare():
    return render_template("compare.html", title="Сравнение")

if __name__ == "__main__":
    app.run(debug=True)
