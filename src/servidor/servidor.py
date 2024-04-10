import socket
import os
from termcolor import colored
import json
import logging

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

def login_usuario(conn, request):
    json_formatado = json.loads(request)
    email = json_formatado['email']
    senha = json_formatado['senha']

    # Carregar usuários do arquivo JSON
    with open('registros/usuarios.json', 'r') as arquivo:
        usuarios = json.load(arquivo)

    # Verificar se o usuário existe e a senha está correta
    for usuario in usuarios:
        if usuario['email'] == email and usuario['senha'] == senha:
            print("Login bem sucedido!")
            conn.send("Login bem sucedido!".encode())
            return True
    
    # Se não encontrar um usuário correspondente ou a senha estiver incorreta
    print("Usuário ou senha incorretos.")
    conn.send("Usuário ou senha incorretos.".encode())
    return False


def adicionar_permission(nome_arquivo, nova_permission):
    # Carregar o arquivo JSON existente
    with open('arquivo.json', 'r') as file:
        dados = json.load(file)
    
    # Encontrar o item correspondente ao nome do arquivo
    for item in dados:
        if item["nome_arquivo"] == nome_arquivo:
            # Adicionar a nova permissão à lista de permissões
            item["permissions"].append(nova_permission)
            break # Encontrou o item, então pode parar de procurar
    
    # Salvar a lista atualizada de volta ao arquivo JSON
    with open('arquivo.json', 'w') as file:
        json.dump(dados, file, indent=4)


def adicionar_novo_dado(nome_arquivo, email, permissions):
    # Carregar o arquivo JSON existente
    with open('arquivo.json', 'r') as file:
        dados = json.load(file)
    
    # Criar um novo dicionário com os dados do novo item
    novo_dado = {
        "nome_arquivo": nome_arquivo,
        "email": email,
        "permissions": permissions
    }
    
    # Adicionar o novo item à lista de dados
    dados.append(novo_dado)
    
    # Salvar a lista atualizada de volta ao arquivo JSON
    with open('arquivo.json', 'w') as file:
        json.dump(dados, file, indent=4)


# Recebe o arquivo do cliente via socket e salva no servidor.
def receive_file(conn, filename,email_usuario):
    file_path = os.path.join("arquivos - servidor", filename)
    with open(file_path, "wb") as file:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            file.write(data)
        print(f"Arquivo {filename} recebido e salvo com sucesso.")
        file.close()
    adicionar_novo_dado(filename,email_usuario,[""])


# Envia o arquivo solicitado para o cliente.
def send_file(conn, filename):
    try:
        # Verifica se o arquivo não é privado (não começa com "privado_")
        if not filename.startswith("privado_"):
            with open("arquivos - servidor/" + filename, "rb") as file:
                for data in file.readlines():
                    conn.send(data)
                print (data)
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

            codigo  = request.split()
            codigo = codigo[0]

            if not request:
                break
            elif codigo == "exit" or codigo == "list":
                if codigo == "exit":  # da erro
                    break
                elif codigo == "list":  # da erro
                    list_files(conn)
            else:
                if codigo == "register":
                    json_str = request.split(" ", 1)   
                    json =  json_str[1]
                    registrar_usuario(conn, json)
                elif codigo == "login":
                    json_str = request.split(" ", 1)   
                    json =  json_str[1]
                    login_usuario(conn,json)
                elif codigo == "download":
                    codigo, filename = request.split()
                    send_file(conn, filename)
                    conn.close()
                elif codigo == "upload":

                    receive_file(conn, json_str,email)
                elif codigo == "privar":
                    upload_file  = request.split()
                    upload_file = upload_file[1]
                    priv_file(conn, upload_file)
        except ConnectionResetError:
            print("Conexão fechada pelo cliente.")
        finally:
            conn.close()
            print(f"Conexão encerrada com {addr}")


if __name__ == "__main__":
    server()
