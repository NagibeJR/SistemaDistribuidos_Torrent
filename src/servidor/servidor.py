import socket
import os
from termcolor import colored
import json
import logging
import threading


def primeiro_list():
    # Carregar os dados do JSON a partir do arquivo
    permissions_file = 'registros/logs_arquivo.json'
    try:
        with open(permissions_file, 'r') as file:
            dados = json.load(file)
    except FileNotFoundError:
        print(f"Arquivo '{permissions_file}' não encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro ao decodificar o JSON.")
        return

    # Listar os arquivos disponíveis com base nas permissões
    public_files = []
    private_files = []
    for item in dados:
        if not item["permissions"]:  # Se as permissões estiverem vazias, o arquivo é público
            public_files.append(item["nome_arquivo"])
        else:
            private_files.append(item["nome_arquivo"])

    print(colored("Arquivos Públicos:", "blue"))
    for file in public_files:
        print(colored(file, "light_blue"))
    
    print(colored("\nArquivos Privados:", "red"))
    for file in private_files:
        print(colored(file, "light_red"))

    file_list = "\n".join(public_files)


# Lista todos os arquivos no diretório do servidor e envia a lista para o cliente.
def list_files(conn):
    # Carregar os dados do JSON a partir do arquivo
    permissions_file = 'registros/logs_arquivo.json'
    try:
        with open(permissions_file, 'r') as file:
            dados = json.load(file)
    except FileNotFoundError:
        print(f"Arquivo '{permissions_file}' não encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro ao decodificar o JSON.")
        return

    # Listar os arquivos disponíveis com base nas permissões
    public_files = []
    private_files = []
    for item in dados:
        if not item["permissions"]:  # Se as permissões estiverem vazias, o arquivo é público
            public_files.append(item["nome_arquivo"])
        else:
            private_files.append(item["nome_arquivo"])

    print(colored("Arquivos Públicos:", "blue"))
    for file in public_files:
        print(colored(file, "light_blue"))
    
    print(colored("\nArquivos Privados:", "red"))
    for file in private_files:
        print(colored(file, "light_red"))

    file_list = "\n".join(public_files)
    conn.sendall(file_list.encode())

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


def adicionar_permission(conn,nome_arquivo, nova_permission):
    # Carregar o arquivo JSON existente
    with open('registros/logs_arquivo.json', 'r') as file:
        dados = json.load(file)
    
    # Encontrar o item correspondente ao nome do arquivo
    for item in dados:
        if item["nome_arquivo"] == nome_arquivo:
            # Adicionar a nova permissão à lista de permissões
            item["permissions"].append(nova_permission)
            break # Encontrou o item, então pode parar de procurar
            
    
    # Salvar a lista atualizada de volta ao arquivo JSON
    with open('registros/logs_arquivo.json', 'w') as file:
        json.dump(dados, file, indent=4)
    conn.send("Arquivo privado com sucesso.".encode())
    
    


def adicionar_novo_dado(nome_arquivo, email, permissions):
    # Carregar o arquivo JSON existente
    with open('registros/logs_arquivo.json', 'r') as file:
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
    with open('registros/logs_arquivo.json', 'w') as file:
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
    adicionar_novo_dado(filename,email_usuario,[])




def send_file(conn, filename, email):
    try:
        # Carregar a lista de arquivos e permissões
        with open('registros/logs_arquivo.json', 'r') as file:
            dados = json.load(file)
        
        # Verifica se o arquivo solicitado existe e se o usuário tem permissão para baixá-lo
        for item in dados:
            if item["nome_arquivo"] == filename:
                if not item["permissions"] or email in item["permissions"]:
                    caminho_completo = os.path.join("arquivos - servidor", filename)
                    if os.path.exists(caminho_completo):
                        conn.send("Enviando".encode())
                        with open(caminho_completo, "rb") as file_to_send:
                            data = file_to_send.read(4096)
                            while data:
                                conn.send(data)
                                data = file_to_send.read(4096)
                        conn.send("EOF".encode())  # Marcador de fim de arquivo
                        print(f"Arquivo {filename} enviado.")
                        return
                else:
                    conn.send("Acesso negado.".encode())
                    return
        # Se o loop terminar sem retornar, o arquivo não foi encontrado ou o usuário não tem permissão
        conn.send("Arquivo não encontrado ou acesso negado.".encode())

    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}")
        conn.send(f"Erro ao enviar o arquivo.".encode())





# função para processar a solicitação de tornar um arquivo privado
def priv_file(conn, filename,email):
    try:
        if os.path.exists(os.path.join("arquivos - servidor", filename)): 
            print(f"Arquivo '{filename}' tornou-se privado.")
            adicionar_permission(conn,filename,email)
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
active_threads = []

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(colored(f"Servidor escutando em {host}:{port}", "grey"))

    while True:
        conn, addr = server.accept()
        print(f"Conexão estabelecida com {addr}")

        # Inicia uma nova thread para lidar com o cliente
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        # Adiciona a nova thread à lista de threads ativas
        active_threads.append(thread)
    


# Listar os arquivos ao iniciar o servidor
def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    try:
        while True:
            # Attempt to receive data from the client
            try:
                request = conn.recv(1024).decode()
                if not request:
                    break
            except OSError as e:
                print(f"Erro ao receber dados do cliente: {e}")
                break

            print("PRINT DA REQUEST SENDO FEITA", request)

            codigo  = request.split()
            codigo = codigo[0]

            # Restante do código de processamento de solicitação aqui...
            
            if codigo == "exit" or codigo == "list":
                if codigo == "exit":
                    break
                elif codigo == "list":
                    list_files(conn)
            else:
                if codigo == "register":
                    json_str = request.split(" ", 1)   
                    json_data =  json_str[1]
                    registrar_usuario(conn, json_data)
                elif codigo == "login":
                    json_str = request.split(" ", 1)   
                    json_data =  json_str[1]
                    login_usuario(conn, json_data)
                elif codigo == "download":
                    comando, Nome_arquivo, email = request.split(" ", 2)
                    send_file(conn, Nome_arquivo, email)
                    conn.send(b"__EOF__")
                elif codigo == "upload":
                    comando, Nome_arquivo, email = request.split(" ", 2)
                    print(Nome_arquivo)
                    print(email)
                    receive_file(conn, Nome_arquivo, email)
                elif codigo == "privar":
                    comando, Nome_arquivo, email = request.split(" ", 2)
                    priv_file(conn, Nome_arquivo, email)
                elif codigo == "autorizar":
                    comando, Nome_arquivo, email = request.split(" ", 2)
                    adicionar_permission(conn, Nome_arquivo, email)
    except ConnectionResetError:
        print("Conexão fechada pelo cliente.")
    finally:
        conn.close()
        print(f"Conexão encerrada com {addr}")


# Inicia o servidor.
def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(colored(f"Servidor escutando em {host}:{port}", "grey"))

    while True:
        conn, addr = server.accept()
        # Cria uma nova thread para lidar com a conexão
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server("localhost", 57000)