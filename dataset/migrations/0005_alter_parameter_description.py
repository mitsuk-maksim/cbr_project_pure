# Generated by Django 3.2.7 on 2021-10-29 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0004_alter_parameter_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='description',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Описание параметра'),
        ),
    ]
