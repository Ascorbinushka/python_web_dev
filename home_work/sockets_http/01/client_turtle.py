import socket
import turtle

# Настройка окна и черепахи
screen = turtle.Screen()
screen.setup(600, 600)
t = turtle.Turtle("turtle")
t.speed(0)
t.color("blue")

# Настройка сокета
HOST = "127.0.0.1"
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Функции движения (локально + отправка на сервер)
def move_up():
    t.setheading(90)
    t.forward(10)
    client_socket.send(b"UP")

def move_down():
    t.setheading(270)
    t.forward(10)
    client_socket.send(b"DOWN")

def move_left():
    t.setheading(180)
    t.forward(10)
    client_socket.send(b"LEFT")

def move_right():
    t.setheading(0)
    t.forward(10)
    client_socket.send(b"RIGHT")

# Управление клавишами
screen.onkey(move_up, "Up")
screen.onkey(move_down, "Down")
screen.onkey(move_left, "Left")
screen.onkey(move_right, "Right")
screen.listen()

screen.mainloop()
client_socket.close()
