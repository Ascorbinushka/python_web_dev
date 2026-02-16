from fastapi import APIRouter, HTTPException, Depends, Query

from schemas import *
from database import UserRepository as ur

from database import QuizRepository as qr
from database import QuestionRepository as qsr
# pip install fastapi_filter
from fastapi_filter import FilterDepends

default_router = APIRouter()

users_router = APIRouter(
    prefix="/users",
    tags = ["Пользователи"]
)

quizes_router = APIRouter(
    prefix="/quizes",
    tags = ["Квизы"]
)

questions_router = APIRouter(
    prefix="/questions",
    tags = ["Вопросы"]
)



@default_router.get('/', tags=['API V1'])
async def index():    
    return {'data':'ok'}



# ответ в виде одиночного списка
@users_router.get('')
async def users_get(
            limit:int = Query(ge=1, lt=10, default=3), 
            offset:int = Query(ge=0, default=0),
            # user_filter: UserFilter = FilterDepends(UserFilter)
        ) -> dict[str, int | list[User]]: 
     
    # users =   await ur.get_users(limit, offset, user_filter)
    users =   await ur.get_users(limit, offset)
    
    # return users
    
    # с развернутым ответом 
    return {"data":users, "limit":limit, "offset":offset}


@users_router.get('/u2')
async def users_get2() -> dict[str, list[User] | str]: 
    users =   await ur.get_users()
    return {'status':'ok', 'data':users}


@users_router.get('/{id}')
async def user_get(id: int) -> User :  
    user =   await ur.get_user(id)
    if user:
        return user    
    raise HTTPException(status_code=404, detail="User not found")
    # или return {'err':"User not found, ..."} # но тогда get_user(id) -> User | dict[str,str]
    
    
@users_router.post('')
async def add_user(user:UserAdd = Depends()) -> UserId:
    id = await ur.add_user(user)
    return {'id':id}    



# ===== КВИЗЫ (новые эндпоинты) =====

@quizes_router.get('')
async def quizes_get(
            limit:int = Query(ge=1, lt=50, default=10), 
            offset:int = Query(ge=0, default=0)
        ) -> dict[str, int | list[Quiz]]:
    """
    Получить список квизов с пагинацией
    
    Args:
        limit: Количество квизов на странице (1-50)
        offset: Смещение (сколько квизов пропустить)
        
    Returns:
        Словарь с данными квизов и параметрами пагинации
    """
    quizes = await qr.get_quizzes(limit, offset)
    return {"data": quizes, "limit": limit, "offset": offset}


@quizes_router.post('')
async def add_quiz(quiz: QuizAdd = Depends()) -> QuizId:
    """
    Создать новый квиз
    
    Args:
        quiz: Данные квиза (название, ID пользователя)
        
    Returns:
        ID созданного квиза
    """
    id = await qr.add_quiz(quiz.model_dump())
    return {'id': id}


@quizes_router.get('/{id}')
async def quiz_get(id: int) -> Quiz:
    """
    Получить квиз по ID
    
    Args:
        id: ID квиза
        
    Returns:
        Данные квиза
    """
    quiz = await qr.get_quiz(id)
    if quiz:
        return quiz
    raise HTTPException(status_code=404, detail="Quiz not found")


@quizes_router.get('/{id}/questions')
async def quiz_questions_list(id: int) -> dict[str, list[Question]]:
    """
    Получить список вопросов конкретного квиза
    
    Args:
        id: ID квиза
        
    Returns:
        Список вопросов принадлежащих квизу
    """
    questions = await qr.get_quiz_questions(id)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this quiz or quiz not exists")
    return {"data": questions}


# ===== ВОПРОСЫ (новые эндпоинты) =====

@questions_router.get('')
async def questions_get(
            limit:int = Query(ge=1, lt=50, default=10), 
            offset:int = Query(ge=0, default=0)
        ) -> dict[str, int | list[Question]]:
    """
    Получить список вопросов с пагинацией
    
    Args:
        limit: Количество вопросов на странице (1-50)
        offset: Смещение (сколько вопросов пропустить)
        
    Returns:
        Словарь с данными вопросов и параметрами пагинации
    """
    questions = await qsr.get_questions(limit, offset)
    return {"data": questions, "limit": limit, "offset": offset}


@questions_router.post('')
async def add_question(question: QuestionAdd = Depends()) -> QuestionId:
    """
    Создать новый вопрос
    
    Args:
        question: Данные вопроса (текст, ответы, ID квиза)
        
    Returns:
        ID созданного вопроса
    """
    id = await qsr.add_question(question.model_dump())
    return {'id': id}


@questions_router.get('/{id}')
async def question_get(id: int) -> Question:
    """
    Получить вопрос по ID
    
    Args:
        id: ID вопроса
        
    Returns:
        Объект вопроса
    """
    question = await qsr.get_question(id)
    if question:
        return question
    raise HTTPException(status_code=404, detail="Question not found")

# async def users_get(
#             limit:int = Query(ge=1, lt=10, default=3), 
#             offset:int = Query(ge=0, default=0),
#             # user_filter: UserFilter = FilterDepends(UserFilter)
#         ) -> dict[str, int | list[User]]: 
     
#     # users =   await ur.get_users(limit, offset, user_filter)
#     users =   await ur.get_users(limit, offset)




# пример развернутого ответа
#     {
            # "items": [...],
            # "total": 100,
            # "page": 1,
            # "size": 10,
            # "pages": 10
            # }

            # Или с ссылками:

            # {
            # "items": [...],
            # "total": 100,
            # "page": 1,
            # "size": 10,
            # "pages": 10,
            # "links": {
            # "next": "http://api.example.com/items?page=2",
            # "prev": null,
            # "first": "http://api.example.com/items?page=1",
            # "last": "http://api.example.com/items?page=10"
            # }
            # }