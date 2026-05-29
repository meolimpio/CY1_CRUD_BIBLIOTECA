from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('livros', '0002_emprestimos_reservas_quantidade_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livro',
            name='quantidade_total',
            field=models.PositiveIntegerField(default=1, verbose_name='quantidade total'),
        ),
    ]
