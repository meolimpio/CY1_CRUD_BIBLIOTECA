"""Views function-based do CRUD de biblioteca."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import EmprestimoForm, LivroForm, LoginForm, ReservaForm
from .models import Emprestimo, Livro, MovimentacaoLivro, Reserva


def registrar_movimentacao(livro, usuario, tipo_movimentacao, descricao='', titulo_livro=None):
    """Cria um registro de histórico para uma ação realizada em um livro."""
    MovimentacaoLivro.criar(
        livro=livro,
        usuario=usuario,
        tipo_movimentacao=tipo_movimentacao,
        descricao=descricao,
        titulo_livro=titulo_livro,
    )


def renderizar_formulario_livro(request, form, titulo_pagina, subtitulo_pagina, texto_botao, livro=None):
    contexto = {
        'form': form,
        'titulo_pagina': titulo_pagina,
        'subtitulo_pagina': subtitulo_pagina,
        'texto_botao': texto_botao,
    }
    if livro is not None:
        contexto['livro'] = livro
    return render(request, 'livros/form_livro.html', contexto)


def obter_resumo_acervo():
    """Calcula os indicadores do acervo com base no estoque e nas movimentações ativas."""
    total_livros = Livro.objects.count()
    total_exemplares = Livro.objects.aggregate(total=Sum('quantidade_total'))['total'] or 0
    total_emprestados = Emprestimo.objects.filter(data_devolucao__isnull=True).count()
    total_reservados = Reserva.objects.filter(status=Reserva.STATUS_ATIVA).count()

    return {
        'total_livros': total_livros,
        'total_exemplares': total_exemplares,
        'total_disponiveis': max(total_exemplares - total_emprestados - total_reservados, 0),
        'total_emprestados': total_emprestados,
        'total_reservados': total_reservados,
    }


def livros_com_totais(queryset=None):
    queryset = queryset or Livro.objects.all()
    return queryset.annotate(
        total_emprestimos_ativos=Count(
            'emprestimos',
            filter=Q(emprestimos__data_devolucao__isnull=True),
            distinct=True,
        ),
        total_reservas_ativas=Count(
            'reservas',
            filter=Q(reservas__status=Reserva.STATUS_ATIVA),
            distinct=True,
        ),
    )


def login_usuario(request):
    """Exibe e processa a tela de login."""
    if request.user.is_authenticated:
        return redirect('lista_livros')

    form = LoginForm(request, data=request.POST or None)

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
    """Lista livros com busca textual e disponibilidade calculada."""
    termo_busca = request.GET.get('q', '').strip()

    livros = livros_com_totais()

    if termo_busca:
        livros = livros.filter(
            Q(titulo__icontains=termo_busca)
            | Q(autor__icontains=termo_busca)
            | Q(editora__icontains=termo_busca)
            | Q(categoria__icontains=termo_busca)
        )

    contexto = {
        'livros': livros,
        'termo_busca': termo_busca,
        **obter_resumo_acervo(),
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

    return renderizar_formulario_livro(
        request,
        form,
        titulo_pagina='Cadastrar novo livro',
        subtitulo_pagina='Preencha os dados principais do livro para adicioná-lo ao acervo.',
        texto_botao='Cadastrar livro',
    )


@login_required
def detalhe_livro(request, livro_id):
    """Exibe todas as informações de um livro."""
    livro = get_object_or_404(livros_com_totais(), id=livro_id)
    historico = livro.movimentacoes.select_related('usuario')[:8]
    emprestimos_ativos = livro.emprestimos.filter(data_devolucao__isnull=True).select_related('usuario_responsavel')
    reservas_ativas = livro.reservas.filter(status=Reserva.STATUS_ATIVA).select_related('usuario_responsavel')

    return render(request, 'livros/detalhe_livro.html', {
        'livro': livro,
        'historico': historico,
        'emprestimos_ativos': emprestimos_ativos,
        'reservas_ativas': reservas_ativas,
    })


@login_required
def editar_livro(request, livro_id):
    """Edita os dados de um livro e registra as movimentações realizadas."""
    livro = get_object_or_404(Livro, id=livro_id)

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

            messages.success(request, 'Livro editado com sucesso.')
            return redirect('detalhe_livro', livro_id=livro_editado.id)
        messages.error(request, 'Não foi possível editar o livro. Verifique os campos destacados.')
    else:
        form = LivroForm(instance=livro)

    return renderizar_formulario_livro(
        request,
        form,
        livro=livro,
        titulo_pagina='Editar livro',
        subtitulo_pagina='Atualize as informações necessárias e salve as alterações.',
        texto_botao='Salvar alterações',
    )


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

    if tipo in MovimentacaoLivro.tipos_validos():
        movimentacoes = movimentacoes.filter(tipo_movimentacao=tipo)

    return render(request, 'livros/historico_movimentacoes.html', {
        'movimentacoes': movimentacoes,
        'tipo_selecionado': tipo,
        'tipo_choices': MovimentacaoLivro.TIPO_CHOICES,
    })


@login_required
def listar_emprestimos(request):
    """Exibe e registra empréstimos."""
    form = EmprestimoForm(request.POST or None, initial={'livro': request.GET.get('livro')})

    if request.method == 'POST':
        if form.is_valid():
            emprestimo = form.save(commit=False)
            emprestimo.usuario_responsavel = request.user
            emprestimo.save()
            registrar_movimentacao(
                livro=emprestimo.livro,
                usuario=request.user,
                tipo_movimentacao=MovimentacaoLivro.TIPO_EMPRESTIMO,
                descricao=(
                    f'O livro "{emprestimo.livro.titulo}" foi emprestado para '
                    f'{emprestimo.nome_leitor}.'
                ),
            )
            messages.success(request, 'Empréstimo registrado com sucesso.')
            return redirect('listar_emprestimos')
        messages.error(request, 'Não foi possível registrar o empréstimo. Verifique os campos destacados.')

    emprestimos = Emprestimo.objects.select_related('livro', 'usuario_responsavel')

    return render(request, 'livros/lista_emprestimos.html', {
        'form': form,
        'emprestimos': emprestimos,
        **obter_resumo_acervo(),
    })


@login_required
def devolver_emprestimo(request, emprestimo_id):
    """Marca um empréstimo como devolvido."""
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id, data_devolucao__isnull=True)

    if request.method == 'POST':
        emprestimo.data_devolucao = timezone.localdate()
        emprestimo.save(update_fields=['data_devolucao'])
        registrar_movimentacao(
            livro=emprestimo.livro,
            usuario=request.user,
            tipo_movimentacao=MovimentacaoLivro.TIPO_DEVOLUCAO,
            descricao=(
                f'O livro "{emprestimo.livro.titulo}" foi devolvido por '
                f'{emprestimo.nome_leitor}.'
            ),
        )
        messages.success(request, 'Devolução registrada com sucesso.')

    return redirect('listar_emprestimos')


@login_required
def listar_reservas(request):
    """Exibe e registra reservas."""
    form = ReservaForm(request.POST or None, initial={'livro': request.GET.get('livro')})
    status = request.GET.get('status', '').strip()

    if request.method == 'POST':
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario_responsavel = request.user
            reserva.save()
            registrar_movimentacao(
                livro=reserva.livro,
                usuario=request.user,
                tipo_movimentacao=MovimentacaoLivro.TIPO_RESERVA,
                descricao=(
                    f'O livro "{reserva.livro.titulo}" foi reservado para '
                    f'{reserva.nome_leitor}.'
                ),
            )
            messages.success(request, 'Reserva registrada com sucesso.')
            return redirect('listar_reservas')
        messages.error(request, 'Não foi possível registrar a reserva. Verifique os campos destacados.')

    reservas = Reserva.objects.select_related('livro', 'usuario_responsavel')
    if status in Reserva.status_validos():
        reservas = reservas.filter(status=status)

    return render(request, 'livros/lista_reservas.html', {
        'form': form,
        'reservas': reservas,
        'status_selecionado': status,
        'status_choices': Reserva.STATUS_CHOICES,
        **obter_resumo_acervo(),
    })


@login_required
def atualizar_reserva(request, reserva_id, novo_status):
    """Atualiza o status de uma reserva."""
    reserva = get_object_or_404(Reserva, id=reserva_id, status=Reserva.STATUS_ATIVA)

    if request.method == 'POST' and novo_status in [Reserva.STATUS_CANCELADA, Reserva.STATUS_ATENDIDA]:
        reserva.status = novo_status
        reserva.save(update_fields=['status', 'data_atualizacao'])
        acao = 'atendida' if novo_status == Reserva.STATUS_ATENDIDA else 'cancelada'
        registrar_movimentacao(
            livro=reserva.livro,
            usuario=request.user,
            tipo_movimentacao=MovimentacaoLivro.TIPO_RESERVA,
            descricao=f'A reserva do livro "{reserva.livro.titulo}" para {reserva.nome_leitor} foi {acao}.',
        )
        messages.success(request, f'Reserva {acao} com sucesso.')

    return redirect('listar_reservas')
