import socket
import os
from termcolor import colored

def list_files(conn):
    """
    Lista todos os arquivos no diretório do servidor e envia a lista para o cliente.
    """
    files = os.listdir("arquivos - servidor")
    file_list = "\n".join(files)
    conn.sendall(file_list.encode())


def send_file(conn, filename):
    """
    Envia o arquivo solicitado para o cliente.
    """
    try:
        with open(filename, 'rb') as file:
            for i in file.readlines():
                conn.send(i)
        print('Arquivo enviado:', filename)
        file.close()
        conn.send(b"Arquivo enviado com sucesso!")  # Envia mensagem de confirmação para o cliente
    except FileNotFoundError:
        print('Arquivo não encontrado:', filename)
        conn.send(b"Arquivo nao encontrado.")


def receive_file(conn, filename):
    """
    Recebe o arquivo do cliente via socket e salva no servidor.
    """
    with open(filename, "wb") as file:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            file.write(data)
            print(f"Arquivo {filename} recebido e salvo com sucesso.")
            file.close()
            conn.send(b"Arquivo recebido com sucesso!")


def handle_client(conn, addr):
    """
    Lida com a conexão do cliente.
    """
    print(f"Conexão estabelecida com {addr}")
    while True:
        request = conn.recv(1024).decode()
        if not request:
            break
        if request == "exit":
            break
        elif request == "download":
            _, filename = request.split()
            send_file(conn, filename)
        elif request == "receive":
            _, filename = request.split()
            receive_file(conn, filename)
        elif request == "list":
            list_files(conn)
    conn.close()
    print(f"Conexão encerrada com {addr}")


def start_server(host, port):
    """
    Inicia o servidor.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(colored("Servidor escutando em {host}:{port}", "red"))

    # Listar os arquivos ao iniciar o servidor
    print(colored("Arquivos no servidor:","green"))
    files = os.listdir("arquivos - servidor")

    for file in files:
        print(colored(file,"light_magenta"))

    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 57000
    start_server(HOST, PORT)
