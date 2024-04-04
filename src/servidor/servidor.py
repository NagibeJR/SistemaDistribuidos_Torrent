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
        with open("arquivos - servidor/" + filename, "rb") as file:
            for dado in file.readlines():
                conn.send(dado)
        print('Arquivo enviado:', filename)
        file.flush()
        conn.send(b"Arquivo enviado com sucesso!")  # Envia mensagem de confirmação para o cliente
    except FileNotFoundError:
        print('Arquivo não encontrado:', filename)
        conn.send(b"Arquivo nao encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o arquivo: {e}")


def receive_file(conn, filename):
    """
    Recebe o arquivo do cliente via socket e salva no servidor.
    """
    try:
        file_path = os.path.join("arquivos - servidor", filename)
        with open(file_path, "wb") as file:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                file.write(data)
                print(f"Arquivo {filename} recebido e salvo com sucesso.")
            file.flush()
            conn.send(b"Arquivo recebido com sucesso!")
    except Exception as e:
        print(f"Erro durante o recebimento do arquivo '{filename}': {e}")


def handle_client(conn, addr):
    """
    Lida com a conexão do cliente.
    """
    print(f"Conexão estabelecida com {addr}")
    try:
        while True:
            request = conn.recv(1024).decode()
            if not request:
                break
            elif request == "exit" or request == "list":
                if request == "exit":
                    break
                elif request == "list":
                    list_files(conn)
            else:
                codigo, filename = request.split()
                if codigo == "download":
                    send_file(conn, filename)
                if codigo == "upload":
                    receive_file(conn, filename)
    except ConnectionResetError:
        print("Conexão fechada pelo cliente.")
    except Exception as e:
        print(f"Ocorreu um erro durante a comunicação com o cliente: {e}")
    finally:
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
