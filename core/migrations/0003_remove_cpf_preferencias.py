from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_dias_treino_user_grupo_foco_user_meta_peso_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='cpf',
        ),
        migrations.RemoveField(
            model_name='user',
            name='preferencias',
        ),
    ]
