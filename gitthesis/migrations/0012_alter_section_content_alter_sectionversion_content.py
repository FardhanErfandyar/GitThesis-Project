# Generated by Django 5.1.1 on 2024-10-14 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitthesis', '0011_alter_section_content_alter_sectionversion_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sectionversion',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
