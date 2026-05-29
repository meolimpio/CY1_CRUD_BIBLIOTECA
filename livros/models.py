"""Models do sistema de biblioteca."""

from django.conf import settings
from django.db import models


class Livro(models.Model):
    """Representa um livro cadastrado no acervo da biblioteca."""

    titulo = models.CharField('título', max_length=150)
    autor = models.CharField('autor', max_length=120)
    editora = models.CharField('editora', max_length=120)
    categoria = models.CharField('gênero/categoria', max_length=100)
    quantidade_total = models.PositiveIntegerField('quantidade total', default=1)
    capa = models.ImageField('capa do livro', upload_to='capas/', blank=True, null=True)
    data_cadastro = models.DateTimeField('data de cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('última atualização', auto_now=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'

    def __str__(self):
        return self.titulo

    @property
    def quantidade_emprestada(self):
        total = getattr(self, 'total_emprestimos_ativos', None)
        if total is not None:
            return total
        return self.emprestimos.filter(data_devolucao__isnull=True).count()

    @property
    def quantidade_reservada(self):
        total = getattr(self, 'total_reservas_ativas', None)
        if total is not None:
            return total
        return self.reservas.filter(status=Reserva.STATUS_ATIVA).count()

    @property
    def quantidade_disponivel(self):
        disponivel = self.quantidade_total - self.quantidade_emprestada - self.quantidade_reservada
        return max(disponivel, 0)

    @property
    def tem_disponibilidade(self):
        return self.quantidade_disponivel > 0


class Emprestimo(models.Model):
    """Registro de empréstimos feitos a leitores."""

    livro = models.ForeignKey(
        Livro,
        verbose_name='livro',
        on_delete=models.CASCADE,
        related_name='emprestimos',
    )
    nome_leitor = models.CharField('nome do leitor', max_length=120)
    data_emprestimo = models.DateField('data do empréstimo', auto_now_add=True)
    data_prevista_devolucao = models.DateField('data prevista de devolução')
    data_devolucao = models.DateField('data de devolução', blank=True, null=True)
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuário responsável',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    data_registro = models.DateTimeField('data de registro', auto_now_add=True)

    class Meta:
        ordering = ['-data_emprestimo', 'livro__titulo']
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'

    def __str__(self):
        return f'{self.livro} - {self.nome_leitor}'

    @property
    def ativo(self):
        return self.data_devolucao is None


class Reserva(models.Model):
    """Registro de reservas feitas para leitores."""

    STATUS_ATIVA = 'ativa'
    STATUS_CANCELADA = 'cancelada'
    STATUS_ATENDIDA = 'atendida'

    STATUS_CHOICES = [
        (STATUS_ATIVA, 'Ativa'),
        (STATUS_CANCELADA, 'Cancelada'),
        (STATUS_ATENDIDA, 'Atendida'),
    ]

    livro = models.ForeignKey(
        Livro,
        verbose_name='livro',
        on_delete=models.CASCADE,
        related_name='reservas',
    )
    nome_leitor = models.CharField('nome do leitor', max_length=120)
    data_reserva = models.DateField('data da reserva', auto_now_add=True)
    status = models.CharField(
        'status da reserva',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA,
    )
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuário responsável',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    data_atualizacao = models.DateTimeField('última atualização', auto_now=True)

    class Meta:
        ordering = ['-data_reserva', 'livro__titulo']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'{self.livro} - {self.nome_leitor}'

    @property
    def ativa(self):
        return self.status == self.STATUS_ATIVA

    @classmethod
    def status_validos(cls):
        return [choice[0] for choice in cls.STATUS_CHOICES]


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

    @classmethod
    def criar(cls, livro, usuario, tipo_movimentacao, descricao='', titulo_livro=None):
        return cls.objects.create(
            livro=livro,
            titulo_livro=titulo_livro or (livro.titulo if livro else ''),
            usuario=usuario if usuario and usuario.is_authenticated else None,
            tipo_movimentacao=tipo_movimentacao,
            descricao=descricao,
        )

    @classmethod
    def tipos_validos(cls):
        return [choice[0] for choice in cls.TIPO_CHOICES]
