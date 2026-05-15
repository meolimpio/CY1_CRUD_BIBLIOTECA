"""Rotas do app livros."""

from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('', views.lista_livros, name='lista_livros'),
    path('livros/novo/', views.cadastrar_livro, name='cadastrar_livro'),
    path('livros/<int:livro_id>/', views.detalhe_livro, name='detalhe_livro'),
    path('livros/<int:livro_id>/editar/', views.editar_livro, name='editar_livro'),
    path('livros/<int:livro_id>/excluir/', views.excluir_livro, name='excluir_livro'),
    path('historico/', views.historico_movimentacoes, name='historico_movimentacoes'),
]
