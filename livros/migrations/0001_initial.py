# Migração inicial criada para o CRUD de biblioteca.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Livro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=150, verbose_name='título')),
                ('autor', models.CharField(max_length=120, verbose_name='autor')),
                ('editora', models.CharField(max_length=120, verbose_name='editora')),
                ('categoria', models.CharField(max_length=100, verbose_name='gênero/categoria')),
                ('quantidade_exemplares', models.PositiveIntegerField(default=1, verbose_name='quantidade de exemplares')),
                ('status', models.CharField(choices=[('disponivel', 'Disponível'), ('emprestado', 'Emprestado'), ('reservado', 'Reservado')], default='disponivel', max_length=20, verbose_name='status do livro')),
                ('capa', models.ImageField(blank=True, null=True, upload_to='capas/', verbose_name='capa do livro')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='data de cadastro')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='última atualização')),
            ],
            options={
                'verbose_name': 'Livro',
                'verbose_name_plural': 'Livros',
                'ordering': ['titulo'],
            },
        ),
        migrations.CreateModel(
            name='MovimentacaoLivro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo_livro', models.CharField(max_length=150, verbose_name='título do livro')),
                ('tipo_movimentacao', models.CharField(choices=[('cadastro', 'Cadastro'), ('edicao', 'Edição'), ('exclusao', 'Exclusão'), ('alteracao_status', 'Alteração de status'), ('emprestimo', 'Empréstimo'), ('devolucao', 'Devolução'), ('reserva', 'Reserva')], max_length=30, verbose_name='tipo de movimentação')),
                ('descricao', models.TextField(blank=True, verbose_name='descrição')),
                ('data_movimentacao', models.DateTimeField(auto_now_add=True, verbose_name='data da movimentação')),
                ('livro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movimentacoes', to='livros.livro', verbose_name='livro')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='usuário responsável')),
            ],
            options={
                'verbose_name': 'Movimentação de Livro',
                'verbose_name_plural': 'Movimentações de Livros',
                'ordering': ['-data_movimentacao'],
            },
        ),
    ]
