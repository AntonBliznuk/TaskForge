# Generated by Django 5.1.3 on 2024-11-26 10:01

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('discription', models.TextField()),
                ('status', models.CharField(default='posted', max_length=50)),
                ('photo', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
            },
        ),
    ]
