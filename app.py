from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import yadisk
import requests
import json
import io

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Замените на надежный секретный ключ

# Контекстный процессор: передаем переменную now во все шаблоны
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# --- Настройка доступа к Яндекс.Диску ---
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

# Получаем актуальный access_token
ACCESS_TOKEN = get_token(REFRESH_TOKEN)
yadisk_client = yadisk.YaDisk(token=ACCESS_TOKEN)

# Путь на Яндекс.Диске для хранения результатов викторины
YANDEX_RESULTS_PATH = "/Proj/quiz_results.json"

def init_results_file():
    try:
        if not yadisk_client.exists("/Proj"):
            yadisk_client.mkdir("/Proj")
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
    # Подробная информация о хоккее
    content = """
    <h2>История хоккея</h2>
    <p>Хоккей с шайбой зародился в Канаде, где первые матчи проводились на замёрзших озёрах. 
    Со временем игра получила развитие, правила совершенствовались, и сегодня хоккей – это динамичный вид спорта с миллионами поклонников по всему миру.</p>
    <h2>Известные игроки</h2>
    <p>Легендарные имена: Валерий Харламов, Владислав Третьяк, Александр Овечкин и многие другие.</p>
    <h2>Статистика и рекорды</h2>
    <p>Например, самая быстрая шайба летит со скоростью более 190 км/ч.</p>
    <h2>Графики и диаграммы</h2>
    <p>[Здесь можно разместить инфографику или диаграммы, например, результаты матчей и статистику]</p>
    """
    return render_template("hockey.html", title="Хоккей", content=content)

@app.route("/football")
def football():
    # Подробная информация о футболе
    content = """
    <h2>История футбола</h2>
    <p>Футбол – это игра, зародившаяся в Англии и ставшая мировым феноменом. 
    Сегодня футбол – один из самых популярных видов спорта, объединяющий миллионы людей.</p>
    <h2>Знаменитые клубы и игроки</h2>
    <p>Например, «Барселона», «Реал Мадрид», Лионель Месси, Криштиану Роналдо.</p>
    <h2>Правила игры</h2>
    <p>Футбольный матч длится 90 минут, играют 11 человек в каждой команде. Есть множество тактических схем и стратегий.</p>
    <h2>Инфографика</h2>
    <p>[Здесь можно добавить графики, таблицы с результатами, статистику чемпионатов]</p>
    """
    return render_template("football.html", title="Футбол", content=content)

@app.route("/compare")
def compare():
    # Сравнение двух видов спорта
    content = """
    <h2>Сравнительный анализ</h2>
    <p>Хоккей и футбол – два динамичных вида спорта, однако у них есть существенные различия:</p>
    <ul>
      <li><strong>Физическая нагрузка:</strong> Хоккей требует высокой выносливости и быстроты реакций, футбол – выносливости и техники владения мячом.</li>
      <li><strong>Тактика:</strong> В хоккее тактические схемы более динамичны, а футбол – стратегически насыщен.</li>
      <li><strong>Оборудование:</strong> Хоккей включает защитную экипировку, футбол – минимальное снаряжение.</li>
    </ul>
    <h2>Диаграммы и графики</h2>
    <p>[Здесь можно разместить сравнительные диаграммы, например, нагрузку на сердце, статистику матчей и рекорды]</p>
    """
    return render_template("compare.html", title="Сравнение", content=content)

@app.route("/quiz")
def quiz():
    # Расширенная викторина с несколькими вопросами
    return render_template("quiz.html", title="Викторина")

# Обработка результатов викторины: проверка ответов, сохранение и вывод
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    # Здесь мы определяем правильные ответы (пример)
    correct_answers = {
        "q1": "hockey",    # Вопрос 1: правильный ответ "hockey"
        "q2": "6",         # Вопрос 2: правильный ответ "6"
        "q3": "11"         # Пример: вопрос 3 (если добавите)
    }
    # Собираем ответы пользователя из формы
    user_answers = {}
    score = 0
    total = 0
    for key in correct_answers:
        total += 1
        answer = request.form.get(key)
        user_answers[key] = answer
        if answer == correct_answers[key]:
            score += 1

    result_text = f"Вы ответили правильно на {score} из {total} вопросов."
    
    # Сохраняем результаты на Яндекс.Диске
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
            "user": request.form.get("username", "Аноним"),
            "score": score,
            "total": total,
            "answers": user_answers,
            "result_text": result_text
        }
        existing_results.append(new_result)
        new_content = json.dumps(existing_results, indent=2)
        stream_upload = io.BytesIO(new_content.encode("utf-8"))
        yadisk_client.upload(stream_upload, YANDEX_RESULTS_PATH, overwrite=True)
        flash("Результаты викторины успешно сохранены!", "success")
    except Exception as e:
        print("Ошибка при сохранении результатов викторины:", e)
        flash("Ошибка при сохранении результатов викторины", "error")
    
    return redirect(url_for("results"))

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
    # Вместо вывода JSON просто красиво оформим данные
    return render_template("results.html", title="Результаты викторины", results=results_data)

if __name__ == "__main__":
    app.run(debug=True)
