# Generated by Django 4.2.4 on 2023-08-05 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='awsuser',
            name='access_key',
            field=models.TextField(max_length=50),
        ),
        migrations.AlterField(
            model_name='awsuser',
            name='secret_key',
            field=models.TextField(max_length=50),
        ),
    ]
