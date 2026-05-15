"""Views function-based do CRUD de biblioteca."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LivroForm
from .models import Livro, MovimentacaoLivro


def registrar_movimentacao(livro, usuario, tipo_movimentacao, descricao='', titulo_livro=None):
    """
    Cria um registro de histórico para uma ação realizada em um livro.

    O parâmetro titulo_livro existe para preservar o nome do livro mesmo quando
    o registro original for excluído do banco de dados.
    """
    MovimentacaoLivro.objects.create(
        livro=livro,
        titulo_livro=titulo_livro or livro.titulo,
        usuario=usuario if usuario.is_authenticated else None,
        tipo_movimentacao=tipo_movimentacao,
        descricao=descricao,
    )


def login_usuario(request):
    """Exibe e processa a tela de login."""
    if request.user.is_authenticated:
        return redirect('lista_livros')

    form = AuthenticationForm(request, data=request.POST or None)

    # Classes CSS aplicadas diretamente nos campos gerados pelo Django.
    form.fields['username'].widget.attrs.update({
        'class': 'campo-formulario',
        'placeholder': 'Digite seu usuário',
        'autocomplete': 'username',
    })
    form.fields['password'].widget.attrs.update({
        'class': 'campo-formulario',
        'placeholder': 'Digite sua senha',
        'autocomplete': 'current-password',
    })

    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Login realizado com sucesso. Bem-vindo(a) à Biblioteca Digital!')
            return redirect('lista_livros')
        messages.error(request, 'Usuário ou senha inválidos. Confira os dados e tente novamente.')

    return render(request, 'livros/login.html', {'form': form})


@login_required
def logout_usuario(request):
    """Encerra a sessão do usuário autenticado."""
    logout(request)
    messages.success(request, 'Você saiu do sistema com segurança.')
    return redirect('login')


@login_required
def lista_livros(request):
    """Lista livros com busca textual e filtro por status."""
    termo_busca = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    livros = Livro.objects.all()

    if termo_busca:
        livros = livros.filter(
            Q(titulo__icontains=termo_busca)
            | Q(autor__icontains=termo_busca)
            | Q(editora__icontains=termo_busca)
            | Q(categoria__icontains=termo_busca)
        )

    status_validos = [choice[0] for choice in Livro.STATUS_CHOICES]
    if status in status_validos:
        livros = livros.filter(status=status)

    resumo_status = Livro.objects.values('status').annotate(total=Count('id'))
    totais_por_status = {item['status']: item['total'] for item in resumo_status}

    contexto = {
        'livros': livros,
        'termo_busca': termo_busca,
        'status_selecionado': status,
        'status_choices': Livro.STATUS_CHOICES,
        'total_livros': Livro.objects.count(),
        'total_disponiveis': totais_por_status.get(Livro.STATUS_DISPONIVEL, 0),
        'total_emprestados': totais_por_status.get(Livro.STATUS_EMPRESTADO, 0),
        'total_reservados': totais_por_status.get(Livro.STATUS_RESERVADO, 0),
    }
    return render(request, 'livros/lista_livros.html', contexto)


@login_required
def cadastrar_livro(request):
    """Cadastra um novo livro no acervo."""
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES)
        if form.is_valid():
            livro = form.save()
            registrar_movimentacao(
                livro=livro,
                usuario=request.user,
                tipo_movimentacao=MovimentacaoLivro.TIPO_CADASTRO,
                descricao=f'O livro "{livro.titulo}" foi cadastrado no acervo.',
            )
            messages.success(request, 'Livro cadastrado com sucesso.')
            return redirect('detalhe_livro', livro_id=livro.id)
        messages.error(request, 'Não foi possível cadastrar o livro. Verifique os campos destacados.')
    else:
        form = LivroForm()

    contexto = {
        'form': form,
        'titulo_pagina': 'Cadastrar novo livro',
        'subtitulo_pagina': 'Preencha os dados principais do livro para adicioná-lo ao acervo.',
        'texto_botao': 'Cadastrar livro',
    }
    return render(request, 'livros/form_livro.html', contexto)


@login_required
def detalhe_livro(request, livro_id):
    """Exibe todas as informações de um livro."""
    livro = get_object_or_404(Livro, id=livro_id)
    historico = livro.movimentacoes.all()[:8]

    return render(request, 'livros/detalhe_livro.html', {
        'livro': livro,
        'historico': historico,
    })


@login_required
def editar_livro(request, livro_id):
    """Edita os dados de um livro e registra as movimentações realizadas."""
    livro = get_object_or_404(Livro, id=livro_id)
    status_anterior = livro.status

    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES, instance=livro)
        if form.is_valid():
            livro_editado = form.save()
            registrar_movimentacao(
                livro=livro_editado,
                usuario=request.user,
                tipo_movimentacao=MovimentacaoLivro.TIPO_EDICAO,
                descricao=f'Os dados do livro "{livro_editado.titulo}" foram editados.',
            )

            if status_anterior != livro_editado.status:
                registrar_movimentacao(
                    livro=livro_editado,
                    usuario=request.user,
                    tipo_movimentacao=MovimentacaoLivro.TIPO_ALTERACAO_STATUS,
                    descricao=(
                        f'O status foi alterado de '
                        f'"{dict(Livro.STATUS_CHOICES).get(status_anterior)}" para '
                        f'"{livro_editado.get_status_display()}".'
                    ),
                )

            messages.success(request, 'Livro editado com sucesso.')
            return redirect('detalhe_livro', livro_id=livro_editado.id)
        messages.error(request, 'Não foi possível editar o livro. Verifique os campos destacados.')
    else:
        form = LivroForm(instance=livro)

    contexto = {
        'form': form,
        'livro': livro,
        'titulo_pagina': 'Editar livro',
        'subtitulo_pagina': 'Atualize as informações necessárias e salve as alterações.',
        'texto_botao': 'Salvar alterações',
    }
    return render(request, 'livros/form_livro.html', contexto)


@login_required
def excluir_livro(request, livro_id):
    """Exibe confirmação e exclui um livro do acervo."""
    livro = get_object_or_404(Livro, id=livro_id)

    if request.method == 'POST':
        titulo = livro.titulo
        registrar_movimentacao(
            livro=livro,
            usuario=request.user,
            tipo_movimentacao=MovimentacaoLivro.TIPO_EXCLUSAO,
            descricao=f'O livro "{titulo}" foi excluído do acervo.',
            titulo_livro=titulo,
        )
        livro.delete()
        messages.success(request, f'O livro "{titulo}" foi excluído com sucesso.')
        return redirect('lista_livros')

    return render(request, 'livros/confirmar_exclusao.html', {'livro': livro})


@login_required
def historico_movimentacoes(request):
    """Exibe o histórico geral de movimentações do sistema."""
    tipo = request.GET.get('tipo', '').strip()
    movimentacoes = MovimentacaoLivro.objects.select_related('livro', 'usuario')

    tipos_validos = [choice[0] for choice in MovimentacaoLivro.TIPO_CHOICES]
    if tipo in tipos_validos:
        movimentacoes = movimentacoes.filter(tipo_movimentacao=tipo)

    return render(request, 'livros/historico_movimentacoes.html', {
        'movimentacoes': movimentacoes,
        'tipo_selecionado': tipo,
        'tipo_choices': MovimentacaoLivro.TIPO_CHOICES,
    })
