# AulaDjango2026 — PersonalPro

Projeto Django desenvolvido em sala de aula, usado como material de acompanhamento e consulta pelos alunos ao longo do curso. O código é construído progressivamente durante as aulas.

**PersonalPro** é um sistema de gestão para personal trainers e alunos: cadastro de alunos e personais, agendamento de sessões e montagem de planos de treino com exercícios.

## 📦 Estrutura do projeto

```
AulaDjango2026/
├── config/         # Configurações do projeto (settings, urls, wsgi/asgi)
├── usuarios/       # Autenticação, perfis de Aluno e Personal
├── agendas/        # Agendamento de sessões entre aluno e personal
├── treinos/        # Exercícios, planos de treino e sessões de treino
├── web/            # Páginas públicas (home, contato)
├── templates/      # Templates globais (base do site)
├── static/         # CSS, JS e imagens
└── manage.py
```

## 🚀 Tecnologias

- Python
- Django 6.0
- SQLite (banco de dados padrão em desenvolvimento)
- Bootstrap (ícones e componentes no front-end)

## 🧩 Apps e funcionalidades

### `usuarios`
Gerencia autenticação e os dois tipos de perfil do sistema:
- **Aluno**: dados pessoais, endereço e objetivo de treino.
- **Personal**: dados pessoais, CREF e especialidade.

Inclui dashboards separados para administrador, aluno e personal, CRUD de alunos e personais, edição de perfil próprio, login customizado e fluxo completo de recuperação de senha (esqueci minha senha, redefinir senha, senha alterada).

Controle de acesso feito com decorators (`usuarios/decorators.py`) e mixins (`usuarios/mixins.py`):
- `superuser_required` — apenas administradores
- `aluno_required` / `AlunoRequiredMixin` — área exclusiva de alunos
- `personal_required` / `PersonalRequiredMixin` — área exclusiva de personais

### `agendas`
Agendamento de sessões entre aluno e personal, com status (`Agendado`, `Realizado`, `Cancelado`), visualização por dia, confirmação e cancelamento de agendamentos.

### `treinos`
Montagem de planos de treino:
- **Exercício**: nome, descrição e grupo muscular.
- **Plano de Treino**: vinculado a um aluno, com período e status (`Ativo`, `Finalizado`, `Cancelado`).
- **Sessão de Treino**: etapas ordenadas dentro de um plano.
- **Sessão de Exercício**: liga exercícios a uma sessão, com séries, repetições, carga e tempo de descanso.

### `web`
Páginas públicas do site: home e contato.

## ⚙️ Como rodar o projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/profAlbertoAyres/AulaDjango2026.git
   cd AulaDjango2026
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux/Mac
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

5. Crie um superusuário para acessar o admin e o dashboard de administrador:
   ```bash
   python manage.py createsuperuser
   ```

6. Rode o servidor local:
   ```bash
   python manage.py runserver
   ```

7. Acesse no navegador:
   ```
   http://127.0.0.1:8000/
   ```

## 📅 Acompanhamento das aulas

O código é atualizado conforme o andamento das aulas. Antes de cada encontro, atualize seu repositório local:

```bash
git pull origin main
```

## 👨‍🏫 Professor

Alberto Ayres

## 📄 Licença

Uso educacional — material de apoio para os alunos.