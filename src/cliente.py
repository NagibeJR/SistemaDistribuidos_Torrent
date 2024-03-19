import socket


def send_file_request(sock, request):
    sock.sendall(request.encode())
    response = sock.recv(1024).decode()
    return response


def download_file(sock, filename):
    with open(filename, "wb") as file:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            file.write(data)


def client():
    name = input("Digite seu nome: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 12345))
    print("Conectado ao servidor.")

    while True:
        print("\nOpções:")
        print("1. Baixar arquivo público")
        print("2. Enviar arquivo privado")
        print("3. Autorizar download de arquivo privado")
        print("4. Privar arquivo")
        print("5. Enviar arquivo para o servidor")
        print("6. Listar arquivos públicos no servidor")
        print("7. Sair")
        option = input("Escolha uma opção: ")

        if option == "1":
            filename = input("Digite o nome do arquivo público que deseja baixar: ")
            response = send_file_request(sock, f"download {filename}")
            if response != "FileNotFound":
                print(f"Baixando o arquivo {filename}...")
                download_file(sock, filename)
                print(f"Arquivo {filename} baixado com sucesso.")
            else:
                print(f"Arquivo {filename} não encontrado no servidor.")

        elif option == "2":
            filename = input("Digite o nome do arquivo privado que deseja enviar: ")
            with open(filename, "rb") as file:
                data = file.read()
            sock.sendall(f"send {filename}".encode())
            sock.sendall(data)
            print(f"Arquivo {filename} enviado para o servidor como privado.")

        elif option == "3":
            filename = input(
                "Digite o nome do arquivo privado que deseja autorizar para download: "
            )
            response = send_file_request(sock, f"authorize {filename}")
            print(response)

        elif option == "4":
            filename = input("Digite o nome do arquivo que deseja privar: ")
            response = send_file_request(sock, f"privatize {filename}")
            print(response)

        elif option == "5":
            filename = input(
                "Digite o nome do arquivo que deseja enviar para o servidor: "
            )
            with open(filename, "rb") as file:
                data = file.read()
            sock.sendall(f"upload {filename}".encode())
            sock.sendall(data)
            print(f"Arquivo {filename} enviado para o servidor.")

        elif option == "6":
            response = send_file_request(sock, "list")
            print("Arquivos públicos no servidor:")
            print(response)

        elif option == "7":
            sock.sendall(b"exit")
            break

        else:
            print("Opção inválida. Tente novamente.")

    sock.close()
    print("Conexão encerrada.")


if __name__ == "__main__":
    client()
