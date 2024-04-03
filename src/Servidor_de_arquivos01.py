import socket
import os
from termcolor import colored

# lista todos os arquivos do servidor
def list_files(conn):
    files = os.listdir("src/Arquivos")
    file_list = "\n".join(files)
    conn.sendall(file_list.encode())



def send_file(conn, filename):
    with open(filename, 'rb') as file:
        for data in file.readlines():
            conn.send(data)
        print('arquivo enviado')

## servidor principal host 

def handle_client(conn, addr):
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
        elif request == "list":
            list_files(conn)
        elif request.startswith("upload"):
            _, filename = request.split()
            with open(os.path.join("arquivos", filename), "wb") as file:
                data = conn.recv(1024)
                while data:
                    file.write(data)
                    data = conn.recv(1024)
            print(f"Arquivo {filename} recebido e salvo com sucesso.")
    conn.close()
    print(f"Conexão encerrada com {addr}")


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(colored("Servidor escutando em {host}:{port}", "red"))

    # Listar os arquivos ao iniciar o servidor
    print(colored("Arquivos no servidor:","green"))
    files = os.listdir("src/Arquivos")
    
    for file in files:
        print(colored(file,"light_magenta"))

    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12345
    start_server(HOST, PORT)
