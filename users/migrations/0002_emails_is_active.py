# Generated by Django 3.2.9 on 2021-11-08 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emails',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
