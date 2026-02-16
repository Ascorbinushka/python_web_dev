'''
1. написать сервер на сокетах который может принимать 3 команды
    - time - отправляет обратно текущее время
    - rnd a:int b:int - отправляет обратно случайное число от а до b (пример - int 1 6)
    - stop - останавливает сервер - отправляет сообщение об этом
    - если прислана неизвестная  команда сообщить об этом клиенту
    
    * на сервере вести лог всех присланных команд в файл 
    
2. написать клиент который запрашивает бесконечно команду для сервера
    и выводит в консоль ответ.

'''

import socket
import datetime
import random
import os
HOST = ('127.0.0.1', 7777)

def log_command(command: str):
    log_path = os.path.join(os.path.dirname(__file__), "server_log.txt")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {command}\n")

def start_server(sock):
    sock.bind(HOST)
    sock.listen()
    print(f"Сервер запущен на {HOST}")

    conn, addr = sock.accept() # залипает на этой строчке и ждет запроса от любого клиента
    with conn:
        print(f"Подключен клиент: {addr}")
        while True:
            data = conn.recv(1024).decode("utf-8").strip()
            if not data:
                break

            log_command(data)  # логируем команды

            if data == "time":
                response = str(datetime.datetime.now())
            elif data.startswith("rnd"):
                try:
                    _, a, b = data.split()
                    a, b = int(a), int(b)
                    response = str(random.randint(a, b))
                except Exception:
                    response = "Ошибка: команда rnd должна быть вида 'rnd a b'"
            elif data == "stop":
                response = "Сервер остановлен"
                conn.sendall(response.encode("utf-8"))
                break
            else:
                response = f"Неизвестная команда: {data}"

            conn.sendall(response.encode("utf-8"))

    print("Сервер завершил работу")

if __name__ == "__main__":
    # SOCK_DGRAM - UDP,  SOCK_STREAM - TCP, AF_INET - ip v4
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_server(sock)
