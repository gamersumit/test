# Generated by Django 4.2.3 on 2024-09-03 10:52

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_alter_logs_images_alter_screencaptures_log_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screencaptures',
            name='image',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]
