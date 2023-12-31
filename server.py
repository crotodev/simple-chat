import socket
import threading

HOST = "127.0.0.1"
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients: list[socket.socket] = []
nicknames: list[bytes] = []


def broadcast(message) -> None:
    for client in clients:
        client.send(message)


def handle(client: socket) -> None:
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]} says {message}")
            broadcast(message)
        except:
            index = client.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


def receive() -> None:
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send("Nick".encode("utf-8"))
        nickname = client.recv(1024)

        clients.append(client)
        nicknames.append(nickname)

        print(f"Client nickname is {nickname}")
        broadcast(f"{nickname} joined.\n".encode("utf-8"))
        client.send("Connected to server.\n".encode("utf-8"))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server started")
receive()
