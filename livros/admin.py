"""Configuração dos models no painel administrativo do Django."""

from django.contrib import admin

from .models import Emprestimo, Livro, MovimentacaoLivro, Reserva


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'autor', 'categoria', 'quantidade_total')
    list_filter = ('categoria',)
    search_fields = ('titulo', 'autor', 'editora', 'categoria')
    readonly_fields = ('data_cadastro', 'data_atualizacao')


@admin.register(MovimentacaoLivro)
class MovimentacaoLivroAdmin(admin.ModelAdmin):
    list_display = ('titulo_livro', 'tipo_movimentacao', 'usuario', 'data_movimentacao')
    list_filter = ('tipo_movimentacao', 'data_movimentacao')
    search_fields = ('titulo_livro', 'descricao', 'usuario__username')
    readonly_fields = ('livro', 'titulo_livro', 'usuario', 'tipo_movimentacao', 'descricao', 'data_movimentacao')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('livro', 'nome_leitor', 'data_emprestimo', 'data_prevista_devolucao', 'data_devolucao')
    list_filter = ('data_emprestimo', 'data_devolucao')
    search_fields = ('livro__titulo', 'nome_leitor')
    readonly_fields = ('data_emprestimo', 'data_registro')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('livro', 'nome_leitor', 'status', 'data_reserva')
    list_filter = ('status', 'data_reserva')
    search_fields = ('livro__titulo', 'nome_leitor')
    readonly_fields = ('data_reserva', 'data_atualizacao')
