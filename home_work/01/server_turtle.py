'''
Написать клиент-серверное приложение использовав библиотеку turtle 
и пример turtle1.py  в котором в рабочем окне на сервере черепаха будет 
повторять все действия которые такая же черепаха производит на клиенте 
под управление пользователя. 


'''



import socket
import turtle

# Настройка окна и черепахи
screen = turtle.Screen()
screen.setup(600, 600)
t = turtle.Turtle("turtle")
t.speed(0)
t.color("red")

# Функции движения
def move_up():
    t.setheading(90)
    t.forward(10)

def move_down():
    t.setheading(270)
    t.forward(10)

def move_left():
    t.setheading(180)
    t.forward(10)

def move_right():
    t.setheading(0)
    t.forward(10)

actions = {
    "UP": move_up,
    "DOWN": move_down,
    "LEFT": move_left,
    "RIGHT": move_right,
}

# Настройка сокета
HOST = "127.0.0.1"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print("Сервер запущен, ожидаем подключения...")
conn, addr = server_socket.accept()
print(f"Подключен клиент: {addr}")

# Получение команд от клиента
while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    if data in actions:
        actions[data]()  # выполнить движение

conn.close()
