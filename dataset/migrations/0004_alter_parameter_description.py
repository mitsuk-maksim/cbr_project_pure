# Generated by Django 3.2.7 on 2021-10-29 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0003_alter_dataset_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='description',
            field=models.CharField(default='', max_length=150, verbose_name='Описание параметра'),
        ),
    ]
