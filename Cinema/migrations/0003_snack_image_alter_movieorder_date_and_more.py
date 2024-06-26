# Generated by Django 5.0.6 on 2024-06-24 16:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cinema', '0002_movieorder_is_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='snack',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='snack_images/'),
        ),
        migrations.AlterField(
            model_name='movieorder',
            name='date',
            field=models.DateField(default=datetime.date(2024, 6, 24)),
        ),
        migrations.AlterField(
            model_name='snackorder',
            name='date',
            field=models.DateField(default=datetime.date(2024, 6, 24)),
        ),
        migrations.AlterField(
            model_name='subscriptionpayment',
            name='date',
            field=models.DateField(default=datetime.date(2024, 6, 24)),
        ),
    ]
