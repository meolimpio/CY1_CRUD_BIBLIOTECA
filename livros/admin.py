"""Configuração dos models no painel administrativo do Django."""

from django.contrib import admin

from .models import Livro, MovimentacaoLivro


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'autor', 'categoria', 'quantidade_exemplares', 'status')
    list_filter = ('status', 'categoria')
    search_fields = ('titulo', 'autor', 'editora', 'categoria')
    readonly_fields = ('data_cadastro', 'data_atualizacao')


@admin.register(MovimentacaoLivro)
class MovimentacaoLivroAdmin(admin.ModelAdmin):
    list_display = ('titulo_livro', 'tipo_movimentacao', 'usuario', 'data_movimentacao')
    list_filter = ('tipo_movimentacao', 'data_movimentacao')
    search_fields = ('titulo_livro', 'descricao', 'usuario__username')
    readonly_fields = ('livro', 'titulo_livro', 'usuario', 'tipo_movimentacao', 'descricao', 'data_movimentacao')
