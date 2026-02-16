import socket
# SOCK_DGRAM - UDP,  SOCK_STREAM - TCP, AF_INET - ip v4
HOST = ('127.0.0.1', 7777)

def start_client(sock):
    sock.connect(HOST)
    print("Клиент подключен к серверу")

    while True:
        cmd = input("Введите команду (time, rnd a b, stop): ")
        sock.sendall(cmd.encode("utf-8"))
        data = sock.recv(1024).decode("utf-8")
        print("Ответ сервера:", data)

        if cmd == "stop":
            break

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_client(sock)
