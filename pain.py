from flask import Flask, render_template, request, make_response, redirect
from markupsafe import escape # для экранирования

import psycopg2
import re  # импорт для регулярных выражений (валидация email)

app = Flask(__name__)

def check_user(login, password):
    # Твой оригинальный код подключения к БД
    conn = psycopg2.connect(
        dbname="SQLiTest",
        user="postgres",
        password="password",
        host="localhost",
        port=3000
    )
    cur = conn.cursor()
    cur.execute('SELECT * FROM "Users" WHERE email=%s AND password_hash=%s', (login, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None

@app.route("/")
def index():
    session_id = request.cookies.get("session_id")
    if session_id == "abc123":
        return redirect("/account")
    else:
        return render_template("index.html")

# Ввод данных для Ввода данных в форму (POST) и получения данных (GET)
@app.route("/auth", methods=["GET", "POST"])
def auth():
    # Получаем логин из URL или из формы
    login = request.args.get("login") or request.form.get("login")
    password = request.args.get("password") or request.form.get("password")

    
    # Проверка email: должен соответствовать формату user@domain.com, серверная валидация
    if not login or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", login): # проверка валидации
        return "Некорректный формат email"
    
    # Проверка пароля: минимальная длина 8 символов, сервеная валидация
    if not password or len(password) < 8:
        return "Пароль слишком короткий (минимум 8 символов)"



    if login and password and check_user(login, password):
        resp = make_response(redirect("/account"))
        resp.set_cookie("session_id", "abc123", httponly=False, secure=True) # Выдача куки, httponly=True - OnlyCookies
        return resp
    else:
        # # XSS уязвимость
        # return f"Пользователь {login} не найден"
    
        # Экранирование данных перед выводом escape(login) превращает специальные символы (<, >, ", ', &) в безопасные HTML‑сущности (&lt;, &gt;, и т.д.).
        return f"Пользователь {escape(login)} не найден" 

@app.route("/account")
def account():
    session_id = request.cookies.get("session_id")
    if session_id == "abc123":
        return "Добро пожаловать в личный кабинет!"
    else:
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
