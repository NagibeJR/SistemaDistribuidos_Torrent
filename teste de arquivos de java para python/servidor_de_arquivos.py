import os
import socket

SERVER_PORT = 12345
DIRETORIO_PADRAO = "src/arquivos"

def main():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', SERVER_PORT))
        server_socket.listen(5)
        print("[Servidor de Arquivos] Aguardando conexões...")

        while True:
            client_socket, address = server_socket.accept()
            handle_client(client_socket, address)
    except Exception as e:
        print(e)
    finally:
        server_socket.close()

def handle_client(client_socket, address):
    try:
        with client_socket, client_socket.makefile('rwb') as reader_writer:
            arquivo_solicitado = reader_writer.readline().decode().strip()
            print(f"Recebida solicitação para o arquivo '{arquivo_solicitado}' de {address}")

            if arquivo_existe(arquivo_solicitado):
                informar_servidor_principal(reader_writer, arquivo_solicitado)
                enviar_arquivo(client_socket, arquivo_solicitado)
            else:
                print(f"Arquivo '{arquivo_solicitado}' não encontrado no servidor {address}")
    except Exception as e:
        print(e)

def arquivo_existe(nome_arquivo):
    caminho_arquivo = os.path.join(DIRETORIO_PADRAO, nome_arquivo)
    return os.path.exists(caminho_arquivo)

def informar_servidor_principal(reader_writer, arquivo):
    response = f"Servidor de arquivos possui o arquivo: {arquivo}\n"
    reader_writer.write(response.encode())
    reader_writer.flush()

def enviar_arquivo(client_socket, arquivo):
    try:
        caminho_arquivo = os.path.join(DIRETORIO_PADRAO, arquivo)
        with open(caminho_arquivo, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client_socket.sendall(data)
        print(f"Arquivo '{arquivo}' enviado para {client_socket.getpeername()[0]}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
