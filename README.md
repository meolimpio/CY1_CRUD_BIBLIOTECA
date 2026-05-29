# CY1_CRUD_BIBLIOTECA

CRUD de biblioteca desenvolvido para o projeto final do módulo 1 do CtrlYoung.
## Funcionalidades

- Login e logout com autenticação do Django
- Cadastro de livros
- Visualização de detalhes
- Edição de dados 
- Upload opcional de capa
- Registro de empréstimos e devoluções
- Registro e acompanhamento de reservas
- Histórico geral de movimentações

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
