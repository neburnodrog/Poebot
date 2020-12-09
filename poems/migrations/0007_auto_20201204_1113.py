# Generated by Django 3.1.3 on 2020-12-04 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poems', '0006_auto_20201129_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='word_gender',
            field=models.CharField(choices=[('MASCULINE', 'MASC'), ('FEMENINE', 'FEM'), ('NONE', 'X')], default='X', max_length=15),
        ),
        migrations.AddField(
            model_name='word',
            name='word_length',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='word',
            name='word_type',
            field=models.CharField(choices=[('ADJECTIVE', 'ADJ'), ('PREPOSITION', 'ADP'), ('ADVERB', 'ADV'), ('VERB', 'VERB'), ('CONJUNCTION', 'CONJ'), ('DETERMINER', 'DET'), ('NOUN', 'NOUN'), ('NUMERAL', 'NUM'), ('PARTICLE', 'PRT'), ('PRONOUN', 'PRON'), ('OTHER', 'X')], default='X', max_length=15),
        ),
    ]