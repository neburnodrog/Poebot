# Generated by Django 3.1.3 on 2020-11-29 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poems', '0003_auto_20201127_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='verse',
            name='verse_is_beg',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verse',
            name='verse_is_end',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verse',
            name='verse_is_int',
            field=models.BooleanField(default=False),
        ),
    ]