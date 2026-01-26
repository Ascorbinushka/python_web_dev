from flask import (Flask, jsonify, render_template, 
                    session, request, redirect, url_for, flash)
import os
import json
from flask_bcrypt import Bcrypt



BASE_DIR = os.path.dirname(__file__) # так работает если проект открыт из любого места


app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))


bcrypt = Bcrypt(app)

# для сессий обязательно
app.config['SECRET_KEY'] = 'my secret key sadj;ask dj;askjd9032094u'


USERS_FILE = os.path.join(BASE_DIR, 'users.json')


# Загружаем пользователей из JSON
def load_users():
    if not os.path.exists(USERS_FILE): # если файла нет, создаём пустой
        save_users([])
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    

# Сохраняем пользователей в JSON
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)



# Вход
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form.get('username', '')
        password_plain = request.form.get('password', '')
        # Ищем первого пользователя с таким логином; если не найден — вернётся None
        user = next((u for u in users if u["username"] == username), None)
        if user is None:
            err = "Неправильный логин"
            print(err)
            return render_template('login.html', err=err) 
        if not bcrypt.check_password_hash(user["password"], password_plain):
            err = "Неправильный пароль"
            return render_template('login.html', err=err, username=username)
        #успешный вход: сохраняем в сессии
        session["logged_in"] = True
        session["username"] = username
        session["fullname"] = f"{user['first_name']} {user['last_name']}"
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/home/')
def home():
    # если пользователь не залогинен — отправляем на форму входа
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # если залогинен — показываем домашнюю страницу
    return render_template("home.html")




# Регистрация
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'login':
            return redirect(url_for('login'))
            
        if action == 'register':
            
            # Загружаем пользователей. Гарантированно вернет [] или существующий список.
            users = load_users()
            
            # Сбор данных
            first_name = request.form.get('first_name', '')
            last_name = request.form.get('last_name', '')
            age = request.form.get('age', '')
            email = request.form.get('email', '')
            username = request.form.get('username', '')
            password_plain = request.form.get('password')
            
            # Хеширование пароля
            password_hash = bcrypt.generate_password_hash(password_plain).decode('utf-8')
            
            # 2. Проверка уникальности
            if any(u["username"] == username for u in users):
                # Вывод ошибки
                err = f"Такой логин ({username}) уже существует"
                return render_template('register.html', err=err,
                                            first_name=first_name,
                                            last_name=last_name,
                                            age=age,
                                            email=email,
                                            username=username
                                       ) 
            
            # Создание нового пользователя
            new_user = {
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                "email": email,
                "username": username,
                "password": password_hash
            }
            
            # Сохранение
            users.append(new_user)
            save_users(users)
            
            return redirect(url_for('login'))
            
    return render_template('register.html')







if __name__ == '__main__':
    app.run(debug=True)
