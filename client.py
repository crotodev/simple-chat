import socket
import threading
import tkinter
from tkinter import scrolledtext, simpledialog

HOST = "127.0.0.1"
PORT = 9090


class Client:
    """
    A client for handling chat in a chat application using sockets and tkinter for GUI.
    """
    def __init__(self, host: str, port: int) -> None:
        """
        Initializes the client with the given host and port, sets up the GUI, and starts the threads for handling GUI and receiving messages.

        :param host: The hostname or IP address of the server.
        :param port: The port number of the server.
        """
        self.win: tkinter.Tk = None
        self.chat_label: tkinter.Label = None
        self.send_button: tkinter.Button = None
        self.input_area: tkinter.Text = None
        self.msg_label: tkinter.Label = None
        self.text_area: scrolledtext.ScrolledText = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self) -> None:
        """
        Sets up the GUI for the chat client. It creates a window with chat history, message input, and send button.
        """
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Comic Sans", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="disabled")

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Comic Sans", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Comic Sans", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self) -> None:
        """
        Sends the message in the input area to the server and clears the input area.
        """
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode("utf-8"))
        self.input_area.delete("1.0", "end")

    def stop(self) -> None:
        """
        Stops the client by ending the main loop, closing the socket, and destroying the GUI window.
        """
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self) -> None:
        """
        Continuously listens for messages from the server and updates the chat history in the GUI.
        """
        while self.running:
            try:
                message = self.sock.recv(1024)
                if message == "NICK":
                    self.sock.send(self.nickname.encode("utf-8"))
                else:
                    if self.gui_done:
                        self.text_area.config(state="normal")
                        self.text_area.insert("end", message)
                        self.text_area.yview("end")
                        self.text_area.config(state="disabled")
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(f"Found {e}")
                self.sock.close()
                break


client = Client(HOST, PORT)
