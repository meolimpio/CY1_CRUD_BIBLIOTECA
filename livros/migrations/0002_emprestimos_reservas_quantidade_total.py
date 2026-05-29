from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('livros', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='livro',
            old_name='quantidade_exemplares',
            new_name='quantidade_total',
        ),
        migrations.RemoveField(
            model_name='livro',
            name='status',
        ),
        migrations.CreateModel(
            name='Emprestimo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_leitor', models.CharField(max_length=120, verbose_name='nome do leitor')),
                ('data_emprestimo', models.DateField(auto_now_add=True, verbose_name='data do empréstimo')),
                ('data_prevista_devolucao', models.DateField(verbose_name='data prevista de devolução')),
                ('data_devolucao', models.DateField(blank=True, null=True, verbose_name='data de devolução')),
                ('data_registro', models.DateTimeField(auto_now_add=True, verbose_name='data de registro')),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emprestimos', to='livros.livro', verbose_name='livro')),
                ('usuario_responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='usuário responsável')),
            ],
            options={
                'verbose_name': 'Empréstimo',
                'verbose_name_plural': 'Empréstimos',
                'ordering': ['-data_emprestimo', 'livro__titulo'],
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_leitor', models.CharField(max_length=120, verbose_name='nome do leitor')),
                ('data_reserva', models.DateField(auto_now_add=True, verbose_name='data da reserva')),
                ('status', models.CharField(choices=[('ativa', 'Ativa'), ('cancelada', 'Cancelada'), ('atendida', 'Atendida')], default='ativa', max_length=20, verbose_name='status da reserva')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='última atualização')),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='livros.livro', verbose_name='livro')),
                ('usuario_responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='usuário responsável')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'ordering': ['-data_reserva', 'livro__titulo'],
            },
        ),
    ]
