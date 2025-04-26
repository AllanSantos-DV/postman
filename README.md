# PyRequestMan - Cliente HTTP em Python

Um cliente HTTP similar ao Postman, desenvolvido inteiramente em Python. Esta aplicação permite testar APIs REST de forma simples e intuitiva, sem necessidade de conexão com serviços externos.

## Características

- Interface gráfica construída com PyQt5
- Suporte para todos os métodos HTTP (GET, POST, PUT, DELETE, etc.)
- Configuração de cabeçalhos, parâmetros e corpo da requisição
- Visualização formatada de respostas (JSON, XML, HTML)
- Gerenciamento de coleções e histórico de requisições
- Funciona offline e é totalmente portátil

## Requisitos

- Python 3.7 ou superior
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Instale as dependências:

```
pip install -r requirements.txt
```

3. Execute a aplicação:

```
python main.py
```

## Estrutura do Projeto

- `/src` - Código-fonte da aplicação
  - `/ui` - Componentes da interface gráfica
  - `/core` - Lógica de negócio
  - `/models` - Modelos de dados
  - `/utils` - Funções utilitárias
- `/resources` - Recursos como ícones e temas
- `/data` - Diretório para armazenamento local

## Licença

Este projeto é distribuído sob a licença MIT. 