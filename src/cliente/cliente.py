import socket
import dearpygui.dearpygui as dpg
from termcolor import colored
import json
import os

sock = None

def connect_to_server():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 57000))
        dpg.hide_item("connect_window")  # Esconde a janela de conexão
        show_login_screen()  # Mostra a tela de login
    except Exception as e:
        dpg.set_value("connect_status", f"Erro ao conectar: {e}")

def send_login():
    email = dpg.get_value("email_login")
    senha = dpg.get_value("senha_login")
    request = json.dumps({"email": email, "senha": senha})
    sock.send(f"login {request}".encode())
    response = sock.recv(1024).decode()
    print(f"Resposta do servidor: {response}")  # Para fins de debug
    if "Login bem sucedido!" in response:
        show_main_menu()  # Redireciona para o menu principal após login bem-sucedido
    else:
        dpg.set_value("login_status", "Login incorreto. Tente novamente.")


def send_register():
    nome = dpg.get_value("nome_register")
    email = dpg.get_value("email_register")
    senha = dpg.get_value("senha_register")
    request = json.dumps({"nome": nome, "email": email, "senha": senha})
    sock.send(f"register {request}".encode())
    response = sock.recv(1024).decode()
    if "cadastrado" in response:
        show_login_screen()  # Volta para a tela de login após o cadastro
    else:
        dpg.set_value("register_status", "Erro no cadastro. Tente novamente.")

def show_login_screen():
    dpg.configure_item("register_window", show=False)
    dpg.configure_item("login_window", show=True)

def show_register_screen():
    dpg.configure_item("login_window", show=False)
    dpg.configure_item("register_window", show=True)

def listar_arquivos():
    # Envia o comando para listar arquivos ao servidor
    sock.sendall("list".encode())
    response = sock.recv(4096).decode()  # Aumente o buffer se necessário, dependendo do tamanho da resposta

    # Atualiza a GUI com a resposta recebida
    atualizar_lista_arquivos_gui(response)

def atualizar_lista_arquivos_gui(lista_arquivos):
    # Identificador da janela que lista os arquivos
    window_tag = "arquivos_list_window"
    
    # Remove a janela anterior, se existir
    if dpg.does_item_exist(window_tag):
        dpg.delete_item(window_tag)
    
    # Cria uma nova janela para listar os arquivos
    with dpg.window(label="Lista de Arquivos", tag=window_tag):
        # Separa os nomes dos arquivos, assumindo que vêm separados por nova linha
        arquivos = lista_arquivos.split('\n')
        for arquivo in arquivos:
            if arquivo:  # Verifica se o nome do arquivo não está vazio
                dpg.add_text(arquivo)

def listar_arquivos_envio():
    diretorio = 'arquivos_para_enviar'
    try:
        arquivos = [f for f in os.listdir(diretorio) if os.path.isfile(os.path.join(diretorio, f))]
        return arquivos
    except FileNotFoundError:
        print(f"O diretório {diretorio} não foi encontrado.")
        return []


def solicitar_download(email_usuario):
    nome_arquivo = dpg.get_value("input_nome_arquivo_download")
    email_usuario = {email_usuario}  
    baixar_arquivo(nome_arquivo, email_usuario)

def baixar_arquivo(nome_arquivo, email_usuario):
    comando = f"download {nome_arquivo} {email_usuario}".encode()
    sock.sendall(comando)
    
    resposta = sock.recv(1024).decode()
    if resposta.startswith("Enviando"):
        caminho_local_arquivo = f"downloads/{nome_arquivo}"
        with open(caminho_local_arquivo, "wb") as arquivo:
            while True:
                dados = sock.recv(4096)
                if b"__EOF__" in dados:
                    # Encontrou marcador de fim, remove-o dos dados e salva o que veio antes
                    arquivo.write(dados.replace(b"__EOF__", b""))
                    break
                arquivo.write(dados)
        dpg.set_value("download_status", f"Arquivo {nome_arquivo} baixado com sucesso.")
    else:
        dpg.set_value("download_status", f"Erro ao baixar o arquivo: {resposta}")


def show_download_interface(sender, app_data, user_data):
    # Verifica se a janela de download já existe
    if not dpg.does_item_exist("download_window"):
        # Cria uma nova janela para o download se não existir
        with dpg.window(label="Baixar Arquivo", tag="download_window"):
            dpg.add_input_text(label="Nome do Arquivo", tag="input_nome_arquivo_download")
            dpg.add_button(label="Confirmar Download", callback=solicitar_download_callback)
            dpg.add_text("", tag="download_status")
    else:
        # Se a janela já existir, apenas a mostra
        dpg.show_item("download_window")

def solicitar_download_callback(sender, app_data, user_data, email_usuario):
    nome_arquivo = dpg.get_value("input_nome_arquivo_download")
    email_usuario = {email_usuario}  # Substitua pelo email do usuário logado
    baixar_arquivo(nome_arquivo, email_usuario)

def listar_arquivos_envio():
    diretorio = 'arquivos_para_enviar'
    arquivos = [f for f in os.listdir(diretorio) if os.path.isfile(os.path.join(diretorio, f))]
    return arquivos

def enviar_arquivo_selecionado(sender, app_data, user_data, email_usuario):
    caminho_arquivo = os.path.join('arquivos_para_enviar', app_data)
    nome_arquivo = os.path.basename(caminho_arquivo)
    email_usuario = {email_usuario} # Substitua pelo email do usuário logado
    # Substitua esta parte pelo seu método de envio de arquivo atual
    print(f"Enviando {nome_arquivo} de {caminho_arquivo}")

def show_send_file_interface():
    arquivos = listar_arquivos_envio()
    
    with dpg.window(label="Enviar Arquivo", tag="send_file_window"):
        # Cria um combo para listar os arquivos
        if arquivos:
            dpg.add_combo(arquivos, label="Selecione o arquivo", tag="file_selector")
            dpg.add_button(label="Enviar Arquivo Selecionado", callback=enviar_arquivo_selecionado, user_data=dpg.get_value("file_selector"))
            dpg.add_text("", tag="send_file_status")
        else:
            dpg.add_text("Nenhum arquivo disponível para enviar.")

def enviar_arquivo(nome_arquivo, caminho_arquivo, email_usuario):
    comando = f"upload {nome_arquivo} {email_usuario}".encode()
    sock.sendall(comando)
    
    resposta = sock.recv(1024).decode()
    if resposta == "OK":
        with open(caminho_arquivo, 'rb') as file:
            while (data := file.read(4096)):
                sock.sendall(data)
            sock.sendall(b"__EOF__")  # Envio do marcador EOF
        print("Arquivo enviado com sucesso.")
    else:
        print("Erro no upload:", resposta)


def solicitar_envio_arquivo(sender, app_data, user_data, email_usuario):
    caminho_arquivo = dpg.get_value("input_file_path")
    email_usuario = {email_usuario}  # Substitua pelo email do usuário logado
    nome_arquivo = os.path.basename(caminho_arquivo)
    enviar_arquivo(caminho_arquivo, nome_arquivo, email_usuario)

def enviar_arquivo_callback(sender, app_data, user_data, email_usuario):
    caminho_arquivo = dpg.get_value("input_file_path")
    if not os.path.isfile(caminho_arquivo):
        dpg.set_value("send_file_status", "Erro: arquivo não encontrado.")
        print("Erro: arquivo não encontrado.")
        return

    nome_arquivo = os.path.basename(caminho_arquivo)
    email_usuario = {email_usuario}  # Substitua pelo email do usuário logado
    enviar_arquivo(caminho_arquivo, nome_arquivo, email_usuario)

def mostrar_lista_arquivos_para_privar(lista_arquivos):
    # Converter a string de resposta em uma lista de arquivos
    arquivos = lista_arquivos.split('\n')
    
    with dpg.window(label="Privar Arquivo", tag="privar_arquivo_window"):
        for arquivo in arquivos:
            dpg.add_button(label=arquivo, callback=privar_arquivo_selecionado, user_data=arquivo)

def privar_arquivo_selecionado(sender, app_data, user_data):
    nome_arquivo = user_data
    comando = f"privar {nome_arquivo}".encode()
    sock.sendall(comando)
    resposta = sock.recv(1024).decode()
    print(resposta)  # Exibir resposta do servidor na interface, se desejado


def solicitar_lista_arquivos_para_privar():
    sock.sendall("listar_para_privar".encode())  # Envia comando para listar arquivos
    response = sock.recv(4096).decode()  # Aumente o buffer se necessário
    mostrar_lista_arquivos_para_privar(response)


def privar_arquivo(nome_arquivo, email_usuario):
    comando = f"privar {nome_arquivo} {email_usuario}"
    sock.sendall(comando.encode())
    resposta = sock.recv(1024).decode()
    print(resposta)

def autorizar_download(nome_arquivo, email_usuario):
    comando = f"autorizar {nome_arquivo} {email_usuario}"
    sock.sendall(comando.encode())
    resposta = sock.recv(1024).decode()
    print(resposta)

def sair():
    dpg.stop_dearpygui()
    print("Saindo...")

def tratar_resposta_servidor():
    while True:
        resposta = sock.recv(1024).decode()
        if resposta:
            print("Resposta do servidor:", resposta)
            if resposta == "__EOF__":
                break  # Finaliza a leitura se o marcador EOF for recebido



def show_main_menu():
    dpg.hide_item("login_window")  # Esconde a tela de login
    dpg.show_item("main_menu_window")  # Mostra o menu principal

def setup_main_menu():
    with dpg.window(label="Menu Principal", tag="main_menu_window", show=False):
        dpg.add_text("Selecione uma opção:")
        dpg.add_button(label="Listar arquivos públicos no servidor", callback=listar_arquivos)
        dpg.add_button(label="Baixar arquivo público", callback=show_download_interface)
        dpg.add_button(label="Enviar Arquivo", callback=show_send_file_interface)
        dpg.add_button(label="Privar Arquivo", callback=show_janela_privar_arquivo)
        dpg.add_button(label="Autorizar download de arquivo privado", callback=autorizar_download)
        dpg.add_button(label="Sair", callback=sair)

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
def download_file(sock, filename,email):
    sock.send(f"download {filename} {email}".encode())
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
def send_file(sock, filename,email):
    sock.send(f"upload {filename} {email}".encode())
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


def autorizar_download(sock,filenamem, email):
    sock.send(f"autorizar {filenamem} {email}".encode())
    print("Autorizando usuario")
    response = sock.recv(1024).decode()
    if response == "OK":
        print(f"Arquivo '{filenamem}' foi autorizado para {email}.")
    else:
        print(f"Erro ao tornar oo autorizar '{filenamem}' : {response}")

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
            download_file(sock, filename,email)
        # enviar um arquivo privado ou publico
        elif option == "3":
            filename = input("Digite o nome do arquivo que deseja enviar: ")
            print('PRINT DO EMAIL',email)
            send_file(sock, filename,email)
        # opcao para bloquear um arquivo para torna publico
        elif option == "4":
            filename = input("Digite o nome do arquivo que deseja tornar privado: ")
            priv_file(sock, filename,email)
        # opcao para autorizar o downalod de um arquivo
        elif option == "5":
            filename = input("Digite o nome do arquivo que deseja tornar privado: ")
            email = input("Digite o nome do email que deseja autorizar ")
            autorizar_download(sock,filename,email)
        # sair da conexao dos servidores de arquivos
        elif option == "6":
            sock.sendall(b"exit")
            break
        else:
            print("Opção inválida. Tente novamente.")
    sock.close()
    print("Conexão encerrada.")

# Função para enviar o comando de tornar um arquivo privado
def enviar_privar_arquivo(email_usuario):
    nome_arquivo = dpg.get_value("input_nome_arquivo_privar")
    email_usuario = {email_usuario}  # Aqui você pode ajustar para obter o email do usuário atual
    comando = f"privar {nome_arquivo} {email_usuario}".encode()
    sock.sendall(comando)
    
    resposta = sock.recv(1024).decode()
    dpg.set_value("status_privar_arquivo", resposta)  # Atualiza o texto de status com a resposta do servidor

# Função para criar a janela de tornar arquivo privado
def show_janela_privar_arquivo():
    if dpg.does_item_exist("janela_privar_arquivo"):
        dpg.delete_item("janela_privar_arquivo")

    with dpg.window(label="Privar Arquivo", tag="janela_privar_arquivo"):
        dpg.add_input_text(label="Nome do Arquivo", tag="input_nome_arquivo_privar")
        dpg.add_button(label="Privar", callback=enviar_privar_arquivo)
        dpg.add_text("", tag="status_privar_arquivo")

# Menu de opções
def show_options_menu(user_data):
    with dpg.window(label="Menu de Opções", tag="options_window", show=False):
        dpg.add_button(label="Listar Arquivos", callback=lambda: print("Listando arquivos..."))
        dpg.add_button(label="Baixar Arquivo Público", callback=lambda: print("Baixar arquivo..."))
        dpg.add_button(label="Enviar Arquivo", callback=lambda: print("Enviar arquivo..."))
        dpg.add_button(label="Privar Arquivo", callback=lambda: print("Privar arquivo..."))
        dpg.add_button(label="Autorizar Download de Arquivo Privado", callback=lambda: print("Autorizar download..."))
        dpg.add_button(label="Sair", callback=lambda: dpg.stop_dearpygui())

def show_send_file_interface():
    with dpg.window(label="Enviar Arquivo", modal=True, tag="send_file_window"):
        dpg.add_text("Digite o nome do arquivo:")
        dpg.add_input_text(label="Nome do arquivo", tag="input_file_path")
        dpg.add_button(label="Enviar Arquivo", callback=enviar_arquivo_callback)
        dpg.add_text("", tag="send_file_status")

def setup_gui():
    dpg.create_context()

    with dpg.window(label="Conectar ao Servidor", tag="connect_window"):
        dpg.add_button(label="Conectar", callback=connect_to_server)
        dpg.add_text("", tag="connect_status")

    with dpg.window(label="Login", tag="login_window", show=False):
        dpg.add_input_text(label="Email", tag="email_login")
        dpg.add_input_text(label="Senha", tag="senha_login", password=True)
        dpg.add_button(label="Login", callback=send_login)
        dpg.add_text("", tag="login_status")
        dpg.add_button(label="Ir para Cadastro", callback=show_register_screen)

    with dpg.window(label="Cadastro", tag="register_window", show=False):
        dpg.add_input_text(label="Nome", tag="nome_register")
        dpg.add_input_text(label="Email", tag="email_register")
        dpg.add_input_text(label="Senha", tag="senha_register", password=True)
        dpg.add_button(label="Registrar", callback=send_register)
        dpg.add_text("", tag="register_status")
        dpg.add_button(label="Voltar para Login", callback=show_login_screen)

    # Configurações da janela de conexão, login e cadastro...
    setup_main_menu()  # Configura o menu principal

    dpg.create_viewport(title='Cliente Steam Verde', width=600, height=300)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


    dpg.create_viewport(title='Cliente Steam Verde', width=600, height=300)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    with dpg.window(label="Operações com Arquivos", tag="operacoes_arquivos_window"):
        dpg.add_button(label="Listar Arquivos Públicos", callback=listar_arquivos)

    with dpg.window(label="Download de Arquivo"):
        dpg.add_input_text(label="Nome do Arquivo", tag="input_nome_arquivo")
        dpg.add_button(label="Baixar Arquivo", callback=solicitar_download)
    
    dpg.create_viewport(title='Cliente', width=600, height=300)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    setup_gui()
    client()
