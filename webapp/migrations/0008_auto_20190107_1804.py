# Generated by Django 2.1.4 on 2019-01-07 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0007_auto_20190107_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='name',
            field=models.CharField(max_length=30, unique=True, verbose_name='房间名'),
        ),
    ]
