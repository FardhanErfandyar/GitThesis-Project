# Generated by Django 5.1.1 on 2024-10-14 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitthesis', '0008_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='title',
            field=models.CharField(default='Untitled Section', max_length=255),
        ),
    ]
