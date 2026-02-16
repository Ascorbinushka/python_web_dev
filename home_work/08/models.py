from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ===== ТАБЛИЦА СВЯЗЕЙ КВИЗОВ И ВОПРОСОВ =====
quiz_question_association = db.Table('quiz_question_association',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('quiz_id', db.Integer, db.ForeignKey('quizzes.id'), nullable=False),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), nullable=False),
    db.Column('order_index', db.Integer, default=0),
    db.Column('added_at', db.DateTime, default=datetime.utcnow),
    
    db.UniqueConstraint('quiz_id', 'question_id', name='unique_quiz_question')
)

# ===== МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ =====
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_quizzes = db.relationship('Quiz', backref='creator', 
                                    cascade="all, delete, delete-orphan",
                                    lazy='dynamic')
    
    created_questions = db.relationship('Question', backref='user',  # ИСПРАВИЛ: было author
                                     cascade="all, delete, delete-orphan",
                                     lazy='dynamic')
    
    def __init__(self, username: str, email: str) -> None:
        self.username = username
        self.email = email
        
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"

# ===== МОДЕЛЬ КВИЗА =====
class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    questions = db.relationship(
        'Question', 
        secondary=quiz_question_association,
        backref=db.backref('quizzes', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def __init__(self, title: str, creator: User, description: str = None, is_public: bool = False) -> None:
        self.title = title
        self.creator = creator
        self.description = description
        self.is_public = is_public
    
    def add_question(self, question: 'Question', order_index: int = 0):
        """Добавить вопрос в квиз"""
        exists = db.session.query(
            db.exists().where(
                quiz_question_association.c.quiz_id == self.id,
                quiz_question_association.c.question_id == question.id
            )
        ).scalar()
        
        if not exists:
            stmt = quiz_question_association.insert().values(
                quiz_id=self.id,
                question_id=question.id,
                order_index=order_index
            )
            db.session.execute(stmt)
    
    def get_questions_ordered(self):
        """Получить вопросы квиза в правильном порядке"""
        return Question.query.join(
            quiz_question_association
        ).filter(
            quiz_question_association.c.quiz_id == self.id
        ).order_by(
            quiz_question_association.c.order_index
        ).all()
    
    def __repr__(self):
        return f"Quiz(id={self.id}, title='{self.title}')"

# ===== МОДЕЛЬ БЛОКА =====
class Block(db.Model):
    __tablename__ = 'blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='block', 
                              cascade="all, delete, delete-orphan",
                              lazy='dynamic')
    
    def __init__(self, name: str, description: str = None) -> None:
        self.name = name
        self.description = description
        
    def __repr__(self):
        return f"Block(id={self.id}, name='{self.name}')"

# ===== МОДЕЛЬ ГРЕЙДА =====
class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='grade', 
                              cascade="all, delete, delete-orphan",
                              lazy='dynamic')
    
    def __init__(self, name: str, points: int, description: str = None) -> None:
        self.name = name
        self.points = points
        self.description = description
        
    def __repr__(self):
        return f"Grade(id={self.id}, name='{self.name}', points={self.points})"

# ===== МОДЕЛЬ ВОПРОСА =====
class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(200), nullable=False)
    wrong1 = db.Column(db.String(200), nullable=False)
    wrong2 = db.Column(db.String(200), nullable=False)
    wrong3 = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ИСПРАВИЛ: было author_id, стало user_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)
    
    def __init__(self, question_text: str, answer: str, wrong1: str, 
                 wrong2: str, wrong3: str, user: User, block: Block, 
                 grade: Grade, explanation: str = None) -> None:
        self.question_text = question_text
        self.answer = answer
        self.wrong1 = wrong1
        self.wrong2 = wrong2
        self.wrong3 = wrong3
        self.user = user
        self.block = block
        self.grade = grade
        self.explanation = explanation
        
    def __repr__(self):
        return f"Question(id={self.id}, text='{self.question_text[:30]}...')"

def db_add_new_data():
    # Очищаем и создаем базу заново
    db.drop_all()
    db.create_all()
    """Создание демонстрационных данных с полным заполнением"""
    
    print("=== СОЗДАЕМ БАЗУ ДАННЫХ ===")
    
    # === 1. СОЗДАЕМ ПОЛЬЗОВАТЕЛЕЙ ===
    print("\n1. СОЗДАЕМ ПОЛЬЗОВАТЕЛЕЙ:")
    
    users_data = [
        {"username": "admin", "email": "admin@quiz.com"},
        {"username": "python_teacher", "email": "python@school.com"},
        {"username": "math_teacher", "email": "math@school.com"},
        {"username": "student1", "email": "student1@learn.com"},
    ]
    
    users = []
    for user_data in users_data:
        user = User(username=user_data["username"], email=user_data["email"])
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"✅ Создано пользователей: {[u.username for u in users]}")

    # === 2. СОЗДАЕМ БЛОКИ (тематические разделы) ===
    print("\n2. СОЗДАЕМ БЛОКИ:")
    
    blocks_data = [
        {"name": "Базовый синтаксис", "desc": "Основные конструкции Python"},
        {"name": "Функции", "desc": "Работа с функциями"},
        {"name": "ООП", "desc": "Объектно-ориентированное программирование"},
        {"name": "Работа с файлами", "desc": "Чтение и запись файлов"},
        {"name": "Модули", "desc": "Импорт и использование модулей"},
        {"name": "Исключения", "desc": "Обработка ошибок"},
    ]
    
    blocks = []
    for block_data in blocks_data:
        block = Block(name=block_data["name"], description=block_data["desc"])
        blocks.append(block)
        db.session.add(block)
    
    db.session.commit()
    print(f"✅ Создано блоков: {[b.name for b in blocks]}")

    # === 3. СОЗДАЕМ ГРЕЙДЫ (уровни сложности) ===
    print("\n3. СОЗДАЕМ ГРЕЙДЫ:")
    
    grades_data = [
        {"name": "Легкий", "points": 1, "desc": "Базовые вопросы"},
        {"name": "Средний", "points": 2, "desc": "Вопросы средней сложности"},
        {"name": "Сложный", "points": 3, "desc": "Сложные вопросы"},
        {"name": "Экспертный", "points": 5, "desc": "Вопросы для экспертов"},
    ]
    
    grades = []
    for grade_data in grades_data:
        grade = Grade(name=grade_data["name"], points=grade_data["points"], 
                     description=grade_data["desc"])
        grades.append(grade)
        db.session.add(grade)
    
    db.session.commit()
    print(f"✅ Создано грейдов: {[g.name for g in grades]}")

    # === 4. СОЗДАЕМ ВОПРОСЫ (разные пользователи создают вопросы) ===
    print("\n4. СОЗДАЕМ ВОПРОСЫ:")
    
    questions_data = [
        # Вопросы от python_teacher (базовый синтаксис)
        {
            "text": "Что выведет программа: print(2 + 3 * 2)?",
            "answer": "8", "wrong1": "10", "wrong2": "7", "wrong3": "Ошибка",
            "user": users[1], "block": blocks[0], "grade": grades[0],
            "explanation": "Умножение выполняется перед сложением"
        },
        {
            "text": "Какой тип данных у значения: 3.14?",
            "answer": "float", "wrong1": "int", "wrong2": "str", "wrong3": "bool",
            "user": users[1], "block": blocks[0], "grade": grades[0]
        },
        {
            "text": "Что делает оператор '**' в Python?",
            "answer": "Возведение в степень", "wrong1": "Умножение", 
            "wrong2": "Деление", "wrong3": "Остаток от деления",
            "user": users[1], "block": blocks[0], "grade": grades[1]
        },
        
        # Вопросы от python_teacher (функции)
        {
            "text": "Как объявить функцию в Python?",
            "answer": "def function():", "wrong1": "function def():", 
            "wrong2": "function():", "wrong3": "def function:",
            "user": users[1], "block": blocks[1], "grade": grades[0]
        },
        {
            "text": "Что вернет функция: def foo(x, y=10): return x + y\nfoo(5)",
            "answer": "15", "wrong1": "5", "wrong2": "10", "wrong3": "Ошибка",
            "user": users[1], "block": blocks[1], "grade": grades[1]
        },
        
        # Вопросы от python_teacher (ООП)
        {
            "text": "Что такое класс в Python?",
            "answer": "Шаблон для создания объектов", "wrong1": "Функция", 
            "wrong2": "Переменная", "wrong3": "Модуль",
            "user": users[1], "block": blocks[2], "grade": grades[1]
        },
        
        # Вопросы от math_teacher (другой пользователь)
        {
            "text": "Как импортировать модуль math?",
            "answer": "import math", "wrong1": "from math import *", 
            "wrong2": "include math", "wrong3": "require math",
            "user": users[2], "block": blocks[4], "grade": grades[0]
        },
    ]
    
    questions = []
    for i, q_data in enumerate(questions_data):
        question = Question(
            question_text=q_data["text"],
            answer=q_data["answer"],
            wrong1=q_data["wrong1"],
            wrong2=q_data["wrong2"],
            wrong3=q_data["wrong3"],
            user=q_data["user"],
            block=q_data["block"],
            grade=q_data["grade"],
            explanation=q_data.get("explanation")
        )
        questions.append(question)
        db.session.add(question)
    
    db.session.commit()
    print(f"✅ Создано вопросов: {len(questions)}")
    print(f"   Создатели: {set(q.user.username for q in questions)}")

    # === 5. СОЗДАЕМ КВИЗЫ И ДОБАВЛЯЕМ В НИХ ВОПРОСЫ ===
    print("\n5. СОЗДАЕМ КВИЗЫ:")
    
    # Python teacher создает квиз по Python
    python_quiz = Quiz(
        title="Python для начинающих", 
        creator=users[1],
        description="Основы программирования на Python",
        is_public=True
    )
    db.session.add(python_quiz)
    
    # Добавляем вопросы в квиз в определенном порядке
    python_quiz.add_question(questions[0], order_index=0)  # Базовый синтаксис - легкий
    python_quiz.add_question(questions[1], order_index=1)  # Базовый синтаксис - легкий
    python_quiz.add_question(questions[2], order_index=2)  # Базовый синтаксис - средний
    python_quiz.add_question(questions[3], order_index=3)  # Функции - легкий
    python_quiz.add_question(questions[4], order_index=4)  # Функции - средний
    
    # Math teacher создает свой квиз
    math_quiz = Quiz(
        title="Python для математиков",
        creator=users[2],
        description="Математические модули Python",
        is_public=False
    )
    db.session.add(math_quiz)
    
    # Добавляем вопросы в math_quiz
    math_quiz.add_question(questions[6], order_index=0)  # Модули от math_teacher
    math_quiz.add_question(questions[2], order_index=1)   # Базовый синтаксис (вопрос может быть в разных квизах!)
    
    db.session.commit()
    print(f"✅ Создано квизов: {python_quiz.title}, {math_quiz.title}")
    print(f"✅ В квизе '{python_quiz.title}' вопросов: {python_quiz.questions.count()}")
    print(f"✅ В квизе '{math_quiz.title}' вопросов: {math_quiz.questions.count()}")

    # === 6. ПРОВЕРЯЕМ СВЯЗИ И ВЫВОДИМ РЕЗУЛЬТАТЫ ===
    print("\n6. ПРОВЕРЯЕМ СВЯЗИ:")
    
    # Проверяем таблицу связей
    association_count = db.session.query(quiz_question_association).count()
    print(f"✅ Записей в таблице связей: {association_count}")
    
    # Показываем вопросы каждого квиза
    for quiz in [python_quiz, math_quiz]:
        print(f"\n📋 Квиз: {quiz.title} (создатель: {quiz.creator.username})")
        ordered_questions = quiz.get_questions_ordered()
        for i, question in enumerate(ordered_questions, 1):
            print(f"   {i}. {question.question_text[:50]}...")
            print(f"      Блок: {question.block.name}, Грейд: {question.grade.name}")
            print(f"      Автор: {question.user.username}")

    print("\n🎉 Демонстрационные данные успешно созданы!")

# Запуск создания данных
if __name__ == "__main__":
    
    
    # Создаем демонстрационные данные
    db_add_new_data()
