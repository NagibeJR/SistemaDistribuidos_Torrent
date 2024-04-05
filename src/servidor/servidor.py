import socket
import os
from termcolor import colored
import json

# funcao para registro de usuarios 
def registrar_usuario(conn,request):
    json_formatado = json.loads(request)
    novo_usuario = {
        'nome': json_formatado['nome'],
        'email': json_formatado['email'],
        'senha': json_formatado['senha']
    }
    # Verifica se o arquivo de usuários existe
    if not os.path.exists('registros/usuarios.json'):
        with open('registros/usuarios.json', 'w') as arquivo:
            arquivo.write("[]")  # Cria um arquivo vazio se não existir

    # Carrega os usuários do arquivo
    with open('registros/usuarios.json', 'r') as arquivo:
        try:
            usuarios = json.load(arquivo)
        except json.decoder.JSONDecodeError:
            usuarios = []

    # Adiciona o novo usuário à lista de usuários
    usuarios.append(novo_usuario)

    # Escreve a lista de usuários de volta no arquivo
    with open('registros/usuarios.json', 'w') as arquivo:
        json.dump(usuarios, arquivo, indent=4)

    print("Usuário registrado com sucesso!")
    conn.send("Usuario cadastrado".encode())
#Lista todos os arquivos no diretório do servidor e envia a lista para o cliente.
def list_files(conn):
    files = os.listdir("src/arquivos - servidor")
    file_list = "\n".join(files)
    conn.sendall(file_list.encode())


#Recebe o arquivo do cliente via socket e salva no servidor.
def receive_file(conn, filename):
    file_path = os.path.join("arquivos - servidor", filename)
    with open(file_path, "wb") as file:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            file.write(data)
        print(f"Arquivo {filename} recebido e salvo com sucesso.")
        file.close()

#Envia o arquivo solicitado para o cliente.
def send_file(conn, filename):
    try:
        with open("arquivos - servidor/" + filename, "rb") as file:
            for data in file.readlines():
                conn.send(data)
            print("Arquivo enviado:", filename)
    except FileNotFoundError:
        conn.send(b"Arquivo nao encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o arquivo: {e}")


def server():
    HOST = "localhost"
    PORT = 57000
    start_server(HOST, PORT)

#Inicia o servidor.
def start_server(host, port):
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print(colored(f"Servidor escutando em {host}:{port}", "red"))
        hub_server(server)


# Listar os arquivos ao iniciar o servidor
def hub_server(server):
    print(colored("Arquivos no servidor:","green"))
    files = os.listdir("src/arquivos - servidor")

    for file in files:
        print(colored(file,"light_magenta"))

    while True:
        conn, addr = server.accept()
        print(f"Conexão estabelecida com {addr}")

        try:
            
                request = conn.recv(1024).decode()
                print("PRINT DA REQUEST SENDO FEITA",request)
                ## tem que trata esse kanso 
                codigo, json_str = request.split(' ', 1)
                print(codigo)

                if not request:
                    break
                elif codigo == "register":
                    registrar_usuario(conn,json_str)
                elif codigo == "exit":
                        break
                elif codigo == "list":
                    list_files(conn)
                elif codigo == "send":
                    codigo, filename = request.split()
                    send_file(conn, filename)
                    conn.close()
                    print("tamo enviando")
                elif codigo == "upload":
                    receive_file(conn, json_str)
        except ConnectionResetError:
            print("Conexão fechada pelo cliente.")
        finally:
            conn.close()
            print(f"Conexão encerrada com {addr}")

if __name__ == "__main__":
    server()
