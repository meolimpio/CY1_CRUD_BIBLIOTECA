"""Models do sistema de biblioteca."""

from django.conf import settings
from django.db import models


class Livro(models.Model):
    """Representa um livro cadastrado no acervo da biblioteca."""

    STATUS_DISPONIVEL = 'disponivel'
    STATUS_EMPRESTADO = 'emprestado'
    STATUS_RESERVADO = 'reservado'

    STATUS_CHOICES = [
        (STATUS_DISPONIVEL, 'Disponível'),
        (STATUS_EMPRESTADO, 'Emprestado'),
        (STATUS_RESERVADO, 'Reservado'),
    ]

    titulo = models.CharField('título', max_length=150)
    autor = models.CharField('autor', max_length=120)
    editora = models.CharField('editora', max_length=120)
    categoria = models.CharField('gênero/categoria', max_length=100)
    quantidade_exemplares = models.PositiveIntegerField('quantidade de exemplares', default=1)
    status = models.CharField(
        'status do livro',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DISPONIVEL,
    )
    capa = models.ImageField('capa do livro', upload_to='capas/', blank=True, null=True)
    data_cadastro = models.DateTimeField('data de cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('última atualização', auto_now=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'

    def __str__(self):
        return self.titulo


class MovimentacaoLivro(models.Model):
    """Histórico das ações realizadas nos livros."""

    TIPO_CADASTRO = 'cadastro'
    TIPO_EDICAO = 'edicao'
    TIPO_EXCLUSAO = 'exclusao'
    TIPO_ALTERACAO_STATUS = 'alteracao_status'
    TIPO_EMPRESTIMO = 'emprestimo'
    TIPO_DEVOLUCAO = 'devolucao'
    TIPO_RESERVA = 'reserva'

    TIPO_CHOICES = [
        (TIPO_CADASTRO, 'Cadastro'),
        (TIPO_EDICAO, 'Edição'),
        (TIPO_EXCLUSAO, 'Exclusão'),
        (TIPO_ALTERACAO_STATUS, 'Alteração de status'),
        (TIPO_EMPRESTIMO, 'Empréstimo'),
        (TIPO_DEVOLUCAO, 'Devolução'),
        (TIPO_RESERVA, 'Reserva'),
    ]

    livro = models.ForeignKey(
        Livro,
        verbose_name='livro',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes',
    )
    titulo_livro = models.CharField('título do livro', max_length=150)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuário responsável',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tipo_movimentacao = models.CharField(
        'tipo de movimentação',
        max_length=30,
        choices=TIPO_CHOICES,
    )
    descricao = models.TextField('descrição', blank=True)
    data_movimentacao = models.DateTimeField('data da movimentação', auto_now_add=True)

    class Meta:
        ordering = ['-data_movimentacao']
        verbose_name = 'Movimentação de Livro'
        verbose_name_plural = 'Movimentações de Livros'

    def __str__(self):
        return f'{self.get_tipo_movimentacao_display()} - {self.titulo_livro}'
