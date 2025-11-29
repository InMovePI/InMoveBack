from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_chatmessage_options_alter_chatmessage_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_picture',
        ),
    ]
