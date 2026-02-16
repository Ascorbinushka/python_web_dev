from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column, func, select, update

from models import UserOrm, Model, QuestionOrm, QuizOrm
from schemas import *

import os


BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, 'db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
    
DB_PATH = os.path.join(DB_DIR, 'fastapi.db')    

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")
# engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}", echo=True) # echo=True - все sql в консоль
# engine = create_async_engine("sqlite+aiosqlite:///example//fastapi//db//fastapi.db")
# engine = create_async_engine("sqlite+aiosqlite:///db//fastapi.db")

new_session = async_sessionmaker(engine, expire_on_commit=False)
# expire_on_commit=False отключает истечение (сброс) атрибутов объектов после commit() в SQLAlchemy сессии.
# если True - после комита обращение к любому полю создаст новый запрос, если False -возмет из памяти



class  DataRepository:
    @classmethod
    async def create_table(cls):
        async with engine.begin() as conn:
            await conn.run_sync(Model.metadata.create_all)
    
    @classmethod            
    async def delete_table(cls):
        async with engine.begin() as conn:
            await conn.run_sync(Model.metadata.drop_all)     

    @classmethod
    async def add_test_data(cls):
        async with new_session() as session:
            users = [
                UserOrm(name='user1', age=20),
                UserOrm(name='user2', age=30, phone='123456789'),
                UserOrm(name='user3', age=41, phone='11'),
                UserOrm(name='user4', age=42, phone='22'),
                UserOrm(name='user5', age=43, phone='33'),
                UserOrm(name='user6', age=44),
                UserOrm(name='user7', age=45)
            ]
            
                        
            session.add_all(users)            
            
            # flush() - используется для синхронизации изменений с базой данных без завершения транзакции
            # проверяет, что операции (вставка, обновление) не вызывают ошибок
            # Если последующие действия в транзакции зависят от предыдущих изменений, 
            # flush() делает эти изменения видимыми в рамках текущей сессии
            await session.flush() 
            await session.commit()



            # Создаем квизы
            quizzes = [
                QuizOrm(name='Основы Python', user_id=users[0].id),
                QuizOrm(name='Продвинутый Python', user_id=users[0].id),
                QuizOrm(name='Базы данных', user_id=users[1].id),
                QuizOrm(name='Web разработка', user_id=users[2].id),
                QuizOrm(name='Алгоритмы', user_id=users[3].id)
            ]
                  
            session.add_all(quizzes)
            await session.flush() 

                # Создаем вопросы для квизов
            questions = [
                # Вопросы для "Основы Python"
                QuestionOrm(
                    question='Что такое список (list) в Python?',
                    answer='Изменяемая последовательность элементов',
                    wrong1='Неизменяемая последовательность',
                    wrong2='Словарь с ключами',
                    quiz_id=quizzes[0].id
                ),
                QuestionOrm(
                    question='Как создать пустой словарь?',
                    answer='dict() или {}',
                    wrong1='[]',
                    wrong2='set()',
                    quiz_id=quizzes[0].id
                ),
                QuestionOrm(
                    question='Что делает функция len()?',
                    answer='Возвращает длину объекта',
                    wrong1='Удаляет объект',
                    wrong2='Создает копию объекта',
                    quiz_id=quizzes[0].id
                ),
                
                # Вопросы для "Продвинутый Python"
                QuestionOrm(
                    question='Что такое декоратор?',
                    answer='Функция, изменяющая поведение другой функции',
                    wrong1='Тип данных',
                    wrong2='Модуль Python',
                    quiz_id=quizzes[1].id
                ),
                QuestionOrm(
                    question='Что такое генератор?',
                    answer='Функция с yield вместо return',
                    wrong1='Функция с return',
                    wrong2='Класс для создания объектов',
                    quiz_id=quizzes[1].id
                ),
                
                # Вопросы для "Базы данных"
                QuestionOrm(
                    question='Что такое PRIMARY KEY?',
                    answer='Уникальный идентификатор записи',
                    wrong1='Внешний ключ',
                    wrong2='Индекс для поиска',
                    quiz_id=quizzes[2].id
                ),
                QuestionOrm(
                    question='Для чего используется JOIN?',
                    answer='Объединение данных из нескольких таблиц',
                    wrong1='Создание новой таблицы',
                    wrong2='Удаление данных',
                    quiz_id=quizzes[2].id
                ),
                
                # Вопросы для "Web разработка"
                QuestionOrm(
                    question='Что такое HTTP?',
                    answer='Протокол передачи гипертекста',
                    wrong1='Язык программирования',
                    wrong2='База данных',
                    quiz_id=quizzes[3].id
                ),
                QuestionOrm(
                    question='Что делает метод GET?',
                    answer='Запрашивает данные от сервера',
                    wrong1='Отправляет данные на сервер',
                    wrong2='Удаляет данные',
                    quiz_id=quizzes[3].id
                ),
                
                # Вопросы для "Алгоритмы"
                QuestionOrm(
                    question='Что такое Big O notation?',
                    answer='Оценка сложности алгоритма',
                    wrong1='Нотация для баз данных',
                    wrong2='Язык программирования',
                    quiz_id=quizzes[4].id
                ),
                QuestionOrm(
                    question='Какой алгоритм сортировки самый быстрый в среднем?',
                    answer='Quicksort',
                    wrong1='Bubble sort',
                    wrong2='Selection sort',
                    quiz_id=quizzes[4].id
                )
            ]
            await session.flush() 
            session.add_all(questions)
            await session.commit()




class UserRepository:
    
    @classmethod
    async def add_user(cls, user: UserAdd) -> int:
        async with new_session() as session:
            data = user.model_dump() # -> dict
            user = UserOrm(**data)
            session.add(user) # не производит операций с БД только с памятью поэтому синхронно
            await session.flush()
            await session.commit()
            return user.id
            
    @classmethod        
    async def get_users(cls, limit, offset,) -> list[UserOrm]:
        async with new_session() as session:
            
            # query = select(UserOrm)
            query = select(UserOrm).limit(limit).offset(offset)
            
            # query = user_filter.filter(query).limit(limit).offset(offset)
            # query = user_filter.sort(query)
            # query = text(f"SELECT * FROM users WHERE id={id}")
            
            res = await session.execute(query)
            users = res.scalars().all()
            return users
        
    @classmethod
    async def get_user(cls, id) -> UserOrm:
        async with new_session() as session:
            query = select(UserOrm).filter(UserOrm.id==id)
            # query = text(f"SELECT * FROM users WHERE id={id}")
            res = await session.execute(query) 
            user = res.scalars().first()
            return user
        



class QuizRepository:
    """Репозиторий для работы с квизами в базе данных"""
    
    @classmethod
    async def add_quiz(cls, quiz: dict) -> int:
        """
        Добавляет новый квиз в базу данных
        
        Args:
            quiz (dict): Словарь с данными квиза (name, user_id и т.д.)
            
        Returns:
            int: ID созданного квиза
            
        Использует:
            - new_session() для получения асинхронной сессии
            - QuizOrm для создания объекта ORM
            - session.add() для добавления в сессию
            - session.flush() для получения ID
            - session.commit() для сохранения в БД
        """
        async with new_session() as session:
            quiz_orm = QuizOrm(**quiz)
            session.add(quiz_orm)
            await session.flush()  # Получаем ID перед коммитом
            await session.commit()
            return quiz_orm.id
            
    @classmethod        
    async def get_quizzes(cls, limit: int, offset: int) -> list[QuizOrm]:
        """
        Получает список квизов с пагинацией
        
        Args:
            limit (int): Максимальное количество записей
            offset (int): Смещение (сколько записей пропустить)
            
        Returns:
            list[QuizOrm]: Список объектов QuizOrm
            
        Использует:
            - select(QuizOrm) для создания запроса
            - .limit() и .offset() для пагинации
            - session.execute() для выполнения запроса
            - .scalars().all() для получения списка объектов
        """
        async with new_session() as session:
            query = select(QuizOrm).limit(limit).offset(offset)
            res = await session.execute(query)
            quizzes = res.scalars().all()
            return quizzes
        
    @classmethod
    async def get_quiz(cls, id: int) -> QuizOrm:
        """
        Получает квиз по ID
        
        Args:
            id (int): ID квиза для поиска
            
        Returns:
            QuizOrm: Объект квиза или None если не найден
            
        Использует:
            - select(QuizOrm).filter() для фильтрации по ID
            - .first() для получения первого результата
        """
        async with new_session() as session:
            query = select(QuizOrm).filter(QuizOrm.id == id)
            res = await session.execute(query) 
            quiz = res.scalars().first()
            return quiz

    @classmethod
    async def get_quiz_questions(cls, id: int) -> list[QuestionOrm]:
        """
        Получает список вопросов для конкретного квиза
        
        Args:
            id (int): ID квиза
            
        Returns:
            list[QuestionOrm]: Список вопросов принадлежащих квизу
            
        Использует:
            - select(QuestionOrm) с фильтром по quiz_id
            - Обычный SELECT без жадной загрузки
        """
        async with new_session() as session:
            # Прямой запрос к таблице вопросов
            query = select(QuestionOrm).filter(QuestionOrm.quiz_id == id)
            res = await session.execute(query) 
            questions = res.scalars().all()
            return questions

    @classmethod
    async def link_questions_to_quiz(cls, quiz_id: int, question_ids: list[int]) -> bool:
        """
        Связывает вопросы с квизом (устанавливает quiz_id для вопросов)
        
        Args:
            quiz_id (int): ID квиза для привязки
            question_ids (list[int]): Список ID вопросов для связывания
            
        Returns:
            bool: True если связи были установлены, False если нет
            
        Использует:
            - update(QuestionOrm) для массового обновления
            - .where() с .in_() для фильтрации по списку ID
            - .values() для установки нового quiz_id
            - result.rowcount для проверки количества обновленных строк
        """
        async with new_session() as session:
            # Массовое обновление вопросов - устанавливаем им quiz_id
            query = update(QuestionOrm).where(
                QuestionOrm.id.in_(question_ids)
            ).values(quiz_id=quiz_id)
            
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0  # True если были обновлены вопросы


class QuestionRepository:
    """Репозиторий для работы с вопросами в базе данных"""
    
    @classmethod
    async def add_question(cls, question: dict) -> int:
        """
        Добавляет новый вопрос в базу данных
        
        Args:
            question (dict): Словарь с данными вопроса 
                            (question, answer, wrong1, wrong2, quiz_id)
            
        Returns:
            int: ID созданного вопроса
        """
        async with new_session() as session:
            question_orm = QuestionOrm(**question)
            session.add(question_orm)
            await session.flush()
            await session.commit()
            return question_orm.id
            
    @classmethod        
    async def get_questions(cls, limit: int, offset: int) -> list[QuestionOrm]:
        """
        Получает список вопросов с пагинацией
        
        Args:
            limit (int): Максимальное количество записей
            offset (int): Смещение (сколько записей пропустить)
            
        Returns:
            list[QuestionOrm]: Список объектов QuestionOrm
        """
        async with new_session() as session:
            query = select(QuestionOrm).limit(limit).offset(offset)
            res = await session.execute(query)
            questions = res.scalars().all()
            return questions
        
    @classmethod
    async def get_question(cls, id: int) -> QuestionOrm:
        """
        Получает вопрос по ID
        
        Args:
            id (int): ID вопроса для поиска
            
        Returns:
            QuestionOrm: Объект вопроса или None если не найден
        """
        async with new_session() as session:
            query = select(QuestionOrm).filter(QuestionOrm.id == id)
            res = await session.execute(query) 
            question = res.scalars().first()
            return question
