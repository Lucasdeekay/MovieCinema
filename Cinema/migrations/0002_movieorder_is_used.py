# Generated by Django 5.0.6 on 2024-06-16 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cinema', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movieorder',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
    ]