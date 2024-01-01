import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = "127.0.0.1"
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients: list[socket.socket] = []
nicknames: list[bytes] = []


def broadcast(message: str) -> None:
    """
    Sends a message to all connected clients.

    :param message: The message to be sent to all clients.
    """
    for client in clients:
        client.send(message)


def handle(client: socket) -> None:
    """
    Handles a single client connection, receiving messages and broadcasting them.

    :param client: The client socket object.
    """
    while True:
        try:
            message: bytes = client.recv(1024)
            logging.info(f"{nicknames[clients.index(client)]} says {message}")
            broadcast(message)
        except Exception as e:
            logging.error(e)
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


def receive() -> None:
    """
    Accepts new connections from clients and starts a new thread to handle each client.
    """
    while True:
        client, address = server.accept()
        logging.info(f"Connected with {str(address)}")

        client.send("NICK".encode("utf-8"))
        nickname = client.recv(1024)

        clients.append(client)
        nicknames.append(nickname)

        logging.info(f"Client nickname is {nickname}")
        broadcast(f"{nickname} joined.\n".encode("utf-8"))
        client.send("Connected to server.\n".encode("utf-8"))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


logging.info("Server started")
receive()
