import socket
from process_command import process_command

def handle_client(client_socket, client_address, bank):
    print(f"[PŘIPOJENÍ] Klient připojen z {client_address}")
    try:
        buffer = ""
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break

            buffer += chunk.decode('utf-8', errors='ignore')

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.replace("\r", "").strip()

                if len(line) < 2:
                    response = "ER Neúplný příkaz\n"
                else:
                    response = process_command(line, bank) + "\n"

                client_socket.sendall(response.encode('utf-8'))
                print(f"[DEBUG] Příkaz: {repr(line)} => {response.strip()}")

    except Exception as e:
        print(f"[CHYBA] {e}")
    finally:
        client_socket.close()
        print(f"[ODPOJENÍ] Klient z {client_address} odpojen.")
