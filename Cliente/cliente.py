import socket
from termcolor import colored

## sock passa o ip que quer conecatar no servidor e resquest para o tipo de dados que deseja receber tipo a lista de arquivos do servidor "List"
def send_file_request(sock, request):
    sock.sendall(request.encode())
    response = sock.recv(1024).decode()
    return response


def download_file(sock, filename):
    with open(filename, "wb") as file:
        while True:
            data = sock.recv(1000000)
            if not data:
                break
            file.write(data)
    print('recebido')
        


def client():
    name = input("Digite seu nome: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 12345))
    print("Conectado ao servidor.")

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
            response = send_file_request(sock, "list")
            print(colored("Arquivos públicos no servidor:", "magenta"))
            print(colored(response,'dark_grey'))



            filename = str(input("Digite o nome do arquivo público que deseja baixar: "))
            sock.send(f"download {filename}".encode())
            print(sock.send)
            download_file(sock, filename)
            if response != "FileNotFound":
                print(f"Baixando o arquivo {filename}...")
                print(f"Arquivo {filename} baixado com sucesso.")
            else:
                print(f"Arquivo {filename} não encontrado no servidor.")
        # enviar um arquivo privado ou publico
        elif option == "2":
            print("funcao e desenvolvimento")
        # opcao para autorizar o downalod de um arquivo
        elif option == "3":
            print("funcao em desenvolvimento")
        # opcao para bloquear um arquivo para torna publico
        elif option == "4":
            print("funcao em desenvolvimento")
        # lista todos os arquivos do servidor
        elif option == "5":
            response = send_file_request(sock, "list")
            print("Arquivos públicos no servidor:")
            print(response)
        #sair da conexao dos servidores de arquivos
        elif option == "6":
            sock.sendall(b"exit")
            break
        else:
            print("Opção inválida. Tente novamente.")

    sock.close()
    print("Conexão encerrada.")


if __name__ == "__main__":
    client()
