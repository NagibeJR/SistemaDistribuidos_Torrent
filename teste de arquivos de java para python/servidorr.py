import socket

MULTICAST_PORT = 5007

def main():
    try:
        multicast_group = '224.0.0.1'
        multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast_group) + socket.inet_aton('0.0.0.0'))
        multicast_socket.bind(('0.0.0.0', MULTICAST_PORT))

        print("[Servidor Principal] Aguardando solicitações...")

        while True:
            data, address = multicast_socket.recvfrom(1024)
            arquivo_solicitado = data.decode().strip()
            print(f"Recebida solicitação para o arquivo '{arquivo_solicitado}' de {address}")

            servidores_respondendo = busca_servidores_de_arquivos(arquivo_solicitado)

            resposta = ','.join(servidores_respondendo)
            multicast_socket.sendto(resposta.encode(), address)
    except Exception as e:
        print(e)
    finally:
        multicast_socket.close()

def busca_servidores_de_arquivos(arquivo_solicitado):
    servidores_respondendo = []

    # Substitua os IPs pelos endereços reais dos seus servidores de arquivos
    servidores_ips = ["127.0.0.1"]

    for servidor_ip in servidores_ips:
        if arquivo_existe_no_servidor(servidor_ip, arquivo_solicitado):
            servidores_respondendo.append(servidor_ip)

    return servidores_respondendo

def arquivo_existe_no_servidor(servidor_ip, arquivo_solicitado):
    # Lógica para verificar se o arquivo existe no servidor com o IP especificado
    # Implemente de acordo com a estrutura do seu sistema
    return True

if __name__ == "__main__":
    main()
