import socket
import threading
import config
from bank import Bank
from bank_server import handle_client

def get_ip_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def start_server():
    ip_address = get_ip_address()
    bank = Bank(ip_address)

    print(f"[START] Server naslouchá na {config.HOST}:{config.PORT}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config.HOST, config.PORT))
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address, bank))
        thread.start()

if __name__ == "__main__":
    start_server()
