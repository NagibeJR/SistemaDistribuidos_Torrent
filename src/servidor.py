import socket
import os


def send_file(conn, filename):
    try:
        with open(filename, "rb") as file:
            data = file.read()
            conn.sendall(data)
        print(f"Arquivo {filename} enviado com sucesso.")
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        conn.sendall(b"FileNotFound")


def list_files(conn):
    files = os.listdir("src/arquivos")
    file_list = "\n".join(files)
    conn.sendall(file_list.encode())


def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    while True:
        request = conn.recv(1024).decode()
        if not request:
            break
        if request == "exit":
            break
        elif request.startswith("download"):
            _, filename = request.split()
            if os.path.isfile(filename):
                if filename.startswith("privado"):
                    conn.sendall(b"PrivateRequest")
                else:
                    send_file(conn, filename)
            else:
                conn.sendall(b"FileNotFound")
        elif request == "list":
            list_files(conn)
        elif request.startswith("upload"):
            _, filename = request.split()
            with open(os.path.join("src/arquivos", filename), "wb") as file:
                data = conn.recv(1024)
                while data:
                    file.write(data)
                    data = conn.recv(1024)
            print(f"Arquivo {filename} recebido e salvo com sucesso.")
            conn.sendall(b"FileUploaded")
    conn.close()
    print(f"Conexão encerrada com {addr}")


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Servidor escutando em {host}:{port}")

    # Listar os arquivos ao iniciar o servidor
    print("Arquivos no servidor:")
    files = os.listdir("src/arquivos")
    for file in files:
        print(file)

    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12345
    start_server(HOST, PORT)
