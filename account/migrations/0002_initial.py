# Generated by Django 5.0.6 on 2024-11-17 22:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('center', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='e_groups',
            field=models.ManyToManyField(blank=True, to='center.e_groups', verbose_name='Kurslar'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='cashback',
            field=models.ManyToManyField(blank=True, to='account.cashback', verbose_name='Cashback turlari'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.district', verbose_name='Tuman'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.gender', verbose_name='Jins'),
        ),
        migrations.AddField(
            model_name='quarters',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.district', verbose_name='Tuman kodi'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='quarters',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.quarters', verbose_name='Mahalla'),
        ),
        migrations.AddField(
            model_name='district',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.regions', verbose_name='Viloyat kodi'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='regions',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.regions', verbose_name='Viloyat'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='roles',
            field=models.ManyToManyField(blank=True, to='account.roles', verbose_name='Roles'),
        ),
        migrations.AddField(
            model_name='useractivity',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi'),
        ),
    ]