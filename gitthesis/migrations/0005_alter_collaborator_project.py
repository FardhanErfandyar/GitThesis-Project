# Generated by Django 5.1.1 on 2024-10-11 19:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitthesis', '0004_alter_collaborator_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collaborator',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='gitthesis.project'),
            preserve_default=False,
        ),
    ]
