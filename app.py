from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import yadisk
import requests
import json
import io

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Замените на надежный ключ

# Контекстный процессор для передачи переменной now во все шаблоны
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Настройки OAuth для Яндекс.Диска
CLIENT_ID = '2bbef6ae892740418c73d62af8e47366'
CLIENT_SECRET = 'b2af829ef1b2452baf85d9d9532c84ac'
REFRESH_TOKEN = '1:svKccVatTXAPlcLk:1hKw1dEXnFBKQZNpkBD63cAlQM1UwWQxHvDTxfT_k6YT9aGaORbmz7tznGip4rli2vZAqKojNw:y7bb2BfPGWvE-_HiCSIgoA'

def get_token(rt):
    url = "https://oauth.yandex.ru/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': rt,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    r = requests.post(url, data=data)
    if r.status_code == 200:
        return r.json().get('access_token')
    else:
        print("Ошибка получения токена:", r.json())
    return None

# Получаем новый access_token по refresh_token
ACCESS_TOKEN = get_token(REFRESH_TOKEN)
yadisk_client = yadisk.YaDisk(token=ACCESS_TOKEN)

# Путь к файлу с результатами викторины на Яндекс.Диске
YANDEX_RESULTS_PATH = "/Proj/quiz_results.json"

def init_results_file():
    try:
        # Если папка /Proj не существует, создаем её
        if not yadisk_client.exists("/Proj"):
            yadisk_client.mkdir("/Proj")
        # Если файла с результатами нет, создаем пустой JSON-массив
        if not yadisk_client.exists(YANDEX_RESULTS_PATH):
            empty_stream = io.BytesIO("[]".encode("utf-8"))
            yadisk_client.upload(empty_stream, YANDEX_RESULTS_PATH)
    except Exception as e:
        print("Ошибка инициализации файла результатов:", e)

init_results_file()

# Основные маршруты приложения
@app.route("/")
def home():
    return render_template("index.html", title="Главная")

@app.route("/hockey")
def hockey():
    return render_template("hockey.html", title="Хоккей")

@app.route("/football")
def football():
    return render_template("football.html", title="Футбол")

@app.route("/compare")
def compare():
    return render_template("compare.html", title="Сравнение")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html", title="Викторина")

# Обработка данных викторины и сохранение их на Яндекс.Диске
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    quiz_data = request.form.get("quiz_data")
    if not quiz_data:
        flash("Нет данных викторины!", "error")
        return redirect(url_for("quiz"))
    try:
        existing_results = []
        try:
            stream = io.BytesIO()
            yadisk_client.download(YANDEX_RESULTS_PATH, stream)
            stream.seek(0)
            existing_results = json.load(stream)
        except Exception as e:
            print("Ошибка чтения файла результатов:", e)
        
        new_result = {
            "timestamp": datetime.now().isoformat(),
            "data": json.loads(quiz_data)
        }
        existing_results.append(new_result)
        new_content = json.dumps(existing_results, indent=2)
        stream_upload = io.BytesIO(new_content.encode("utf-8"))
        yadisk_client.upload(stream_upload, YANDEX_RESULTS_PATH, overwrite=True)
        
        flash("Результаты успешно сохранены!", "success")
        return redirect(url_for("results"))
    except Exception as e:
        print("Ошибка при обработке результатов:", e)
        flash("Ошибка при сохранении результатов викторины", "error")
        return redirect(url_for("quiz"))

# Отображение результатов викторины
@app.route("/results")
def results():
    try:
        stream = io.BytesIO()
        yadisk_client.download(YANDEX_RESULTS_PATH, stream)
        stream.seek(0)
        results_data = json.load(stream)
    except Exception as e:
        print("Ошибка чтения результатов:", e)
        results_data = []
    return render_template("results.html", title="Результаты викторины", results=results_data)

if __name__ == "__main__":
    app.run(debug=True)
