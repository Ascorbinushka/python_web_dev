from flask import Flask, render_template, request, redirect, url_for, flash
import os
from models import db, db_add_new_data


BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, 'db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
    
DB_PATH = os.path.join(DB_DIR, 'db_quiz.db')    


app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.config['SECRET_KEY'] = 'secretkeysecretkeysecretkey1212121'

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'


db.init_app(app)

html_config = {
    'admin':True,
    'debug':False
}

# операции с БД перед запуском сервера
with app.app_context():
    db_add_new_data()
    # users = User.query.all()
    # users = User.query.filter(User.id>1).all()
    # print(users)
    # user = db.session.get(User, 1)    
    # print(user)
    # print(user.quizes)
  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Здесь будет реальная проверка логина
        if username and password:  # Заглушка - всегда успешно
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # Здесь будет реальная регистрация
        if username and email and password:  # Заглушка - всегда успешно
            flash('Регистрация прошла успешно! Теперь можете войти.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Заполните все поля', 'error')
    return render_template('register.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/start_quiz')
def start_quiz():
    return render_template('start_quiz.html')

@app.route('/quiz_editor')
def quiz_editor():
    return render_template('quiz_editor.html')

@app.route('/admin_editor')
def admin_editor():
    return render_template('admin_editor.html')

if __name__ == '__main__':
    app.run(debug=True)
