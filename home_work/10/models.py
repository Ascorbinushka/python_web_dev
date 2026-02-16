from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column, func

from datetime import datetime

class Model(DeclarativeBase):

    # можно тут добавить тогда эти столбцы будут во всех таблицах
   # т.к. мы наследуемся от этого класса
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # будет вписывать дататайм при создании записи
    dateCreate: Mapped[datetime] = mapped_column(        
                                        server_default=func.now(),
                                        nullable=False)
    
    # будет вписывать дататайм при обновлении записи
    dateUpdate: Mapped[datetime] = mapped_column(        
                                        server_default=func.now(),
                                        server_onupdate=func.now(),
                                        nullable=False)


class UserOrm(Model):
    __tablename__ = 'user'
    
    # уже не нужен так как наследуется
    # id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str]
    age: Mapped[int]
    phone: Mapped[str|None]
    quizzes = relationship('QuizOrm', back_populates='user')


class QuizOrm(Model):
    __tablename__ = 'quiz'
    
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user = relationship('UserOrm', back_populates='quizzes')  
    
    questions = relationship('QuestionOrm', back_populates='quiz')

class QuestionOrm(Model):
    __tablename__ = 'question'
    
    question: Mapped[str]
    answer: Mapped[str]
    wrong1: Mapped[str]
    wrong2: Mapped[str]
    
    quiz_id = mapped_column(ForeignKey('quiz.id'))
    quiz = relationship('QuizOrm', back_populates='questions') 



    