import socket
from termcolor import colored
import json


# Lista os arquivos do servidor.
def list_file(sock, request):
    sock.sendall(request.encode())
    response = sock.recv(1024).decode()
    print("\nArquivos públicos no servidor:")
    print(response)


# envio das informacoes do usuario
def send_user(sock, user_data,option):
    if option =='1':
        option = 'login'
    else:
        option = 'register'
    data = json.dumps(user_data)
    response = sock.send(f"{option} {data}".encode())
    response = sock.recv(1024).decode()
    return response


# Baixa o arquivo do servidor para o cliente via socket.
def download_file(sock, filename):
    sock.send(f"download {filename}".encode())
    response = sock.recv(1024).decode()
    try:
        print(f"Baixando o arquivo {filename}...")
        with open("arquivos - cliente/" + filename, "wb") as file:
            while True:
                data = sock.recv(4096)  # Recebe 1KB de dados do servidor
                if not data:
                    break
                file.write(data)
        print(f"Arquivo '{filename}' recebido com sucesso.")
        file.close()
    except Exception as e:
        print(f"Erro durante o download do arquivo '{filename}': {e}")


# sepossivel usar bites para envio
# Envia o arquivo do cliente para o servidor via socket.
def send_file(sock, filename):
    sock.send(f"upload {filename}".encode())
    try:
        with open("arquivos - cliente/" + filename, "rb") as file:
                for data in file.readlines():
                    sock.send(data)
                print("Arquivo enviado com sucesso!")
        file.close()
    except FileNotFoundError:
        print(f"Arquivo '{filename}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o arquivo: {e}")

# Envia a solicitação para tornar um arquivo privado para o servidor.
def priv_file(sock, filename,email):
    sock.send(f"privar {filename} {email}".encode())
    print(f"Arquivo '{filename}' tornando privado...")
    response = sock.recv(1024).decode()
    if response == "OK":
        print(f"Arquivo '{filename}' tornou-se privado com sucesso.")
    else:
        print(f"Erro ao tornar o arquivo '{filename}' privado: {response}")


##imput do cliente
def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 57000))
    print("Conectado ao servidor principal.")
    print(colored("bem vindo a steam verde\n------------------------ ", "green"))
    print("1- Fazer login")
    print("2- cadastra usuario")

    email = ''
    while True:
        option = input("Escolha a opcao: ")

        if option == "1":
            email = input("Email: ")
            senha = input("Senha: ")
            name = input("Digite seu nome: ")
            break

        elif option == '2':
            email = input("Digite o email:")
            senha = input("Digite a senha:")
            name = input("Digite seu nome: ")
            break
        else:
            print("opcao invalida tente novamente")

    user_data = {
        'nome': name,
        'email': email,
        'senha': senha
    }
    responseee = send_user(sock,user_data,option)
    print(responseee)
    sock.close()

    ##Opções disponiveis
    while True:        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 57000))
        print("Conectado ao servidor.")
        print("\nOpções:")
        print("1. Listar arquivos públicos no servidor")
        print("2. Baixar arquivo público")
        print("3. Enviar arquivo")
        print("4. Privar arquivo")
        print("5. Autorizar download de arquivo privado")
        print("6. Sair")
        option = input("Escolha uma opção: ")
        # baixar os arquivos do servidores
        # lista todos os arquivos do servidor
        if option == "1":
            list_file(sock, "list")

        elif option == "2":
            filename = input("Digite o nome do arquivo público que deseja baixar: ")
            download_file(sock, filename)
        # enviar um arquivo privado ou publico
        elif option == "3":
            filename = input("Digite o nome do arquivo que deseja enviar: ")
            send_file(sock, filename)

        # opcao para bloquear um arquivo para torna publico
        elif option == "4":
            filename = input("Digite o nome do arquivo que deseja tornar privado: ")
            print(email)
            priv_file(sock, filename,email)
        # opcao para autorizar o downalod de um arquivo
        elif option == "5":
            print("funcao e desenvolvimento")
        # sair da conexao dos servidores de arquivos
        elif option == "6":
            sock.sendall(b"exit")
            break
        else:
            print("Opção inválida. Tente novamente.")
    sock.close()
    print("Conexão encerrada.")

if __name__ == "__main__":
    client()
