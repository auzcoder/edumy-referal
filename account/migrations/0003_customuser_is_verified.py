# Generated by Django 5.0.6 on 2024-11-24 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='Tasdiqlangan'),
        ),
    ]
