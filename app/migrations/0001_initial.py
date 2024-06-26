# Generated by Django 5.0.4 on 2024-04-29 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PatentData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('age', models.CharField(max_length=100, null=True)),
                ('medicine', models.CharField(max_length=100, null=True)),
                ('allergy', models.CharField(max_length=100, null=True)),
                ('previous_medication', models.CharField(max_length=100, null=True)),
                ('weight', models.CharField(max_length=100, null=True)),
                ('symptoms', models.TextField(null=True)),
                ('recdata', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
