
# Projeto de Sistemas Distribuídos

Este é um projeto desenvolvido para a disciplina de Sistemas Distribuídos, com o objetivo de criar uma aplicação Peer-to-Peer para o compartilhamento de arquivos entre máquinas. A aplicação permite que um usuário faça upload, download e torne arquivos privados ou autorize outros usuários a baixá-los.

## Estrutura do Projeto

A estrutura do projeto está organizada da seguinte forma:

```
src/
├── arquivos - cliente/
├── arquivos - servidor/
├── cliente/
│   ├── cliente.py
│   └── cliente2.py
├── registros/
│   ├── logs_arquivo.json
│   └── usuarios.json
├── servidor/
│   └── servidor.py
├── .gitignore
└── README.md
```

- **arquivos - cliente/**: Diretório onde os arquivos baixados ou enviados pelo cliente são armazenados.
- **arquivos - servidor/**: Diretório onde os arquivos recebidos pelo servidor são salvos e gerenciados.
- **cliente/**: Contém os scripts `cliente.py` e `cliente2.py`, que implementam a lógica do cliente, permitindo operações de login, cadastro, upload e download de arquivos.
- **registros/**: Contém arquivos JSON para armazenamento de logs e dados dos usuários:
  - `logs_arquivo.json`: Registra os arquivos e suas permissões (público ou privado).
  - `usuarios.json`: Armazena as informações dos usuários registrados.
- **servidor/**: Contém o script `servidor.py`, que implementa a lógica do servidor, gerenciando conexões, autenticação e permissões dos arquivos.

## Funcionalidades

### Cliente

- **Login e Cadastro**: Usuários podem se registrar e fazer login na aplicação.
- **Listar Arquivos Públicos**: Permite ao usuário listar todos os arquivos disponíveis publicamente no servidor.
- **Download de Arquivos**: Usuários podem baixar arquivos públicos ou arquivos privados para os quais têm permissão.
- **Upload de Arquivos**: Permite ao usuário enviar arquivos para o servidor.
- **Privar Arquivo**: O usuário pode tornar um arquivo privado.
- **Autorizar Download**: O usuário pode conceder permissão a outros usuários para baixar um arquivo privado.

### Servidor

- **Gerenciamento de Conexões**: Lida com múltiplas conexões de clientes usando threads.
- **Registro e Autenticação de Usuários**: Gerencia o registro e a autenticação dos usuários.
- **Controle de Acesso a Arquivos**: Gerencia permissões de arquivos, permitindo que arquivos privados sejam baixados apenas por usuários autorizados.
- **Armazenamento de Dados em JSON**: Utiliza arquivos JSON para registrar informações de usuários e permissões de arquivos.

## Como Executar

### Servidor

1. Acesse o diretório `servidor/`.
2. Execute o arquivo `servidor.py` para iniciar o servidor:
   ```bash
   python servidor.py
   ```
   O servidor estará escutando na porta 57000.

### Cliente

1. Acesse o diretório `cliente/`.
2. Execute `cliente.py` ou `cliente2.py` para iniciar um cliente:
   ```bash
   python cliente.py
   ```
3. Siga as instruções exibidas no terminal para login, upload e download de arquivos.

## Tecnologias Utilizadas

- **Python**: Para a implementação do servidor e cliente.
- **Sockets**: Para comunicação entre o cliente e o servidor.
- **Threads**: Para gerenciar múltiplas conexões simultâneas no servidor.
- **JSON**: Para armazenamento de informações dos usuários e permissões de arquivos.
