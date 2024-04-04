import socket
from termcolor import colored

def list_file(sock, request):
    """
    Lista os arquivos do servidor.
    """
    sock.sendall(request.encode())
    response = sock.recv(1024).decode()
    return response


def download_file(sock, filename):
    """
    Baixa o arquivo do servidor para o cliente via socket.
    """
    try:
        with open("arquivos - cliente/" + filename, "wb") as file:
            while True:
                data = sock.recv(4096)  # Recebe 1KB de dados do servidor
                if not data:
                    break
                file.write(data)
        print(f"Arquivo '{filename}' recebido com sucesso.")
        file.flush()
    except Exception as e:
        print(f"Erro durante o download do arquivo '{filename}': {e}")


def send_file(sock, filename):
    """
    Envia o arquivo do cliente para o servidor via socket.
    """
    try:
        with open("arquivos - cliente/" + filename, "rb") as file:
            for dado in file.readlines():
                sock.send(dado)
            print("Arquivo enviado com sucesso!")
            file.flush()

    except FileNotFoundError:
        print(f"Arquivo '{filename}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o arquivo: {e}")

##imput do cliente
def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 57000))
    print("Conectado ao servidor.")
    ##Opções disponiveis
    while True:
        print("\nOpções:")
        print("1. Baixar arquivo público")
        print("2. Enviar arquivo")
        print("3. Autorizar download de arquivo privado")
        print("4. Privar arquivo")
        print("5. Listar arquivos públicos no servidor")
        print("6. Sair")
        option = input("Escolha uma opção: ")
        # baixar os arquivos do servidores
        if option == "1":
            response = list_file(sock, "list")
            print(colored("Arquivos públicos no servidor:", "magenta"))
            print(colored(response,'dark_grey'))
            filename = input("Digite o nome do arquivo público que deseja baixar: ")
            sock.send(f"download {filename}".encode())

            if response != "Arquivo nao encontrado.":
                download_file(sock, filename)
                print(f"Baixando o arquivo {filename}...")
                print(f"Arquivo {filename} baixado com sucesso.")
            else:
                print(f"Arquivo {filename} não encontrado no servidor.")
        # enviar um arquivo privado ou publico
        elif option == "2":
            filename = input("Digite o nome do arquivo que deseja enviar: ")
            sock.send(f"upload {filename}".encode())
            send_file(sock, filename)
        # opcao para autorizar o downalod de um arquivo
        elif option == "3":
            print("funcao e desenvolvimento")
        # opcao para bloquear um arquivo para torna publico
        elif option == "4":
            print("funcao em desenvolvimento")
        # lista todos os arquivos do servidor
        elif option == "5":
            response = list_file(sock, "list")
            print("Arquivos públicos no servidor:")
            print(response)
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
