# Generated by Django 4.2.3 on 2024-09-03 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_rename_user_project_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='images',
            field=models.ManyToManyField(related_name='logs', to='projects.screencaptures'),
        ),
        migrations.AlterField(
            model_name='screencaptures',
            name='log_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screen_captures', to='projects.logs'),
        ),
    ]
