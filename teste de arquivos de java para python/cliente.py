import socket

def main():
    client_socket = None
    try:
        servidor_principal_addr = "127.0.0.1"
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        arquivo_solicitado = input("Digite o nome do arquivo desejado: ")

        send_data = arquivo_solicitado.encode()
        client_socket.sendto(send_data, (servidor_principal_addr, 5007))

        receive_data, _ = client_socket.recvfrom(1024)
        servidores_respondendo = receive_data.decode().split(",")

        if not servidores_respondendo or servidores_respondendo[0] == "":
            print("Nenhum servidor de arquivos possui o arquivo solicitado.")
            return

        print("Servidores de arquivos que possuem o arquivo:")
        for servidor_ip in servidores_respondendo:
            print(servidor_ip)

        servidor_escolhido = input("Digite o IP do servidor escolhido: ")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as download_socket:
            download_socket.connect((servidor_escolhido, 5000))
            with open("C:/Users/logxp/Documents/socket-servidores-de-arquivo/baixados/" + arquivo_solicitado, "wb") as file:
                while True:
                    data = download_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)

        print(f"Arquivo '{arquivo_solicitado}' baixado com sucesso.")

    except Exception as e:
        print(e)
    finally:
        if client_socket:
            client_socket.close()

if __name__ == "__main__":
    main()
