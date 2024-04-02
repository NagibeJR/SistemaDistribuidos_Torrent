import socket
import os


def send_file_request(sock, request):
    sock.sendall(request.encode())
    response = sock.recv(1024).decode()
    return response


def list_client_files():
    client_files = os.listdir("src/clientes_arquivos")
    print("Arquivos disponíveis para envio:")
    for i, filename in enumerate(client_files, start=1):
        print(f"{i}. {filename}")
    return client_files


def upload_file(sock, filename):
    with open(os.path.join("clientes_arquivos", filename), "rb") as file:
        data = file.read()
    sock.sendall(f"upload {filename}".encode())
    sock.sendall(data)
    print(f"Arquivo {filename} enviado para o servidor.")


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
            # Código para baixar arquivo público
            pass
        elif option == "2":
            # Código para enviar arquivo privado
            pass
        elif option == "3":
            # Código para autorizar download de arquivo privado
            pass
        elif option == "4":
            # Código para privar arquivo
            pass
        elif option == "5":
            client_files = list_client_files()
            if client_files:
                choice = int(input("Escolha o número do arquivo que deseja enviar: "))
                if 1 <= choice <= len(client_files):
                    filename = client_files[choice - 1]
                    upload_file(sock, filename)
                else:
                    print("Escolha inválida.")
            else:
                print("Não há arquivos disponíveis para envio.")
        elif option == "6":
            # Código para listar arquivos públicos no servidor
            pass
        elif option == "7":
            sock.sendall(b"exit")
            break
        else:
            print("Opção inválida. Tente novamente.")

    sock.close()
    print("Conexão encerrada.")


if __name__ == "__main__":
    client()
