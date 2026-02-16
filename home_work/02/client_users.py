import socket
import pandas as pd
import os

HOST = ("127.0.0.1", 7777)
EXCEL_FILE = "users.xlsx"

def load_users():
    """Загрузка пользователей из Excel"""
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=["login", "password"])

def save_users(df):
    """Сохранение пользователей в Excel"""
    df.to_excel(EXCEL_FILE, index=False)

def start_client(sock):
    sock.connect(HOST)
    print(f"Клиент подключен к серверу {HOST}")

    # Загружаем таблицу пользователей
    users = load_users()

    # Спрашиваем действие
    action = input("Выберите действие: регистрация (reg) или вход (signin): ").strip()

    login = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()

    if action == "reg":
        # Проверяем, есть ли такой пользователь
        if ((users["login"] == login) & (users["password"] == password)).any():
            print("Такой пользователь уже существует!")
        else:
            # Добавляем нового пользователя
            new_user = pd.DataFrame({"login": [login], "password": [password]})
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            print("Пользователь зарегистрирован!")

        command = f"command:reg; login:{login}; password:{password}"

    elif action == "signin":
        # Проверяем наличие пользователя
        if ((users["login"] == login) & (users["password"] == password)).any():
            print("Вход выполнен успешно!")
            command = f"command:signin; login:{login}; password:{password}"
        else:
            print("Ошибка: такого пользователя нет или пароль неверный")
            return
    else:
        print("Неизвестная команда")
        return

    # Отправляем команду на сервер
    sock.sendall(command.encode("utf-8"))
    data = sock.recv(1024).decode("utf-8")
    print("Ответ сервера:", data)

    sock.close()

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_client(sock)
