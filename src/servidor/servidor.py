import socket
import os
from termcolor import colored
import json

# Lista todos os arquivos no diretório do servidor e envia a lista para o cliente.
def list_files(conn):
    public_files = [
        file
        for file in os.listdir("arquivos - servidor")
        if not file.startswith("privado_")
    ]
    file_list = "\n".join(public_files)
    conn.sendall(file_list.encode())
    print("Lista de arquivos enviada para o cliente.")


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

# Recebe o arquivo do cliente via socket e salva no servidor.
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

# Envia o arquivo solicitado para o cliente.
def send_file(conn, filename):
    try:
        file_path = os.path.join("arquivos - servidor", filename)
        # Verifica se o arquivo não é privado (não começa com "privado_")
        if not filename.startswith("privado_") and os.path.exists(file_path):
            with open("arquivos - servidor/" + filename, "rb") as file:
                for data in file.readlines():
                    conn.send(data)
                print("Arquivo enviado:", filename)
        else:
            conn.send(b"PRIVADO")
    except FileNotFoundError:
        conn.send(b"Arquivo nao encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o arquivo: {e}")


# função para processar a solicitação de tornar um arquivo privado
def priv_file(conn, filename):
    try:
        if os.path.exists(os.path.join("arquivos - servidor", filename)):
            old_path = os.path.join("arquivos - servidor", filename)
            new_path = os.path.join("arquivos - servidor", "privado_" + filename)
            os.rename(old_path, new_path)
            print(f"Arquivo '{filename}' tornou-se privado.")
            conn.send("OK".encode())
        else:
            conn.send("Arquivo não encontrado.".encode())
    except Exception as e:
        conn.send(str(e).encode())
        print(f"Erro ao tornar o arquivo '{filename}' privado:", e)


def server():
    HOST = "localhost"
    PORT = 57000
    start_server(HOST, PORT)

# Inicia o servidor.
def start_server(host, port):
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print(colored(f"Servidor escutando em {host}:{port}", "grey"))
        hub_server(server)


# Listar os arquivos ao iniciar o servidor
def hub_server(server):
    print(colored("\nArquivos no servidor", "green"))
    public_files = []
    private_files = []

    files = os.listdir("arquivos - servidor")
    for file in files:
        if file.startswith("privado_"):
            private_files.append(file[len("privado_") :])
        else:
            public_files.append(file)

    print(colored("Arquivos Públicos:", "blue"))
    for file in public_files:
        print(colored(file, "light_blue"))
    
    print(colored("\nArquivos Privados:", "red"))
    for file in private_files:
        print(colored(file, "light_red"))

    while True:
        conn, addr = server.accept()
        print(f"Conexão estabelecida com {addr}")

        try:

            request = conn.recv(1024).decode()
            print("PRINT DA REQUEST SENDO FEITA", request)

            if not request:
                break
            elif request == "exit" or request == "list":
                if request == "exit":  # da erro
                    break
                elif request == "list":  # da erro
                    list_files(conn)
            else:
                codigo, json_str = request.split(" ", 1)   
                if codigo == "register":
                    registrar_usuario(conn, json_str)
                elif codigo == "download":
                    codigo, filename = request.split()
                    send_file(conn, filename)
                    conn.close()
                elif codigo == "upload":
                    receive_file(conn, json_str)
                elif codigo == "privar":
                    priv_file(conn, json_str)
        except ConnectionResetError:
            print("Conexão fechada pelo cliente.")
        finally:
            conn.close()
            print(f"Conexão encerrada com {addr}")


if __name__ == "__main__":
    server()
