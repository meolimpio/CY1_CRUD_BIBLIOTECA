# CY1_CRUD_BIBLIOTECA — Versão aperfeiçoada

CRUD de biblioteca desenvolvido em Django, Python, HTML, CSS autoral e JavaScript puro.

## Funcionalidades

- Login e logout com autenticação padrão do Django
- Cadastro de livros
- Listagem com busca e filtro por status
- Visualização de detalhes
- Edição de dados e capa
- Exclusão com confirmação
- Upload opcional de capa
- Histórico geral de movimentações
- Histórico por livro na tela de detalhes
- Layout responsivo, acessível e baseado na paleta: `#948D9B`, `#B279A7`, `#D387AB`, `#E899DC`

## Como rodar

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute as migrações:

```bash
python manage.py migrate
```

Crie um usuário administrador:

```bash
python manage.py createsuperuser
```

Rode o servidor:

```bash
python manage.py runserver
```

Acesse:

- Sistema: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Admin: http://127.0.0.1:8000/admin/
