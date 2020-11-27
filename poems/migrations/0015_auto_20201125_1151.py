# Generated by Django 3.1.3 on 2020-11-25 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poems', '0014_word_amount_verses'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assonantrhyme',
            options={'ordering': ['assonant_rhyme']},
        ),
        migrations.AlterModelOptions(
            name='consonantrhyme',
            options={'ordering': ['consonant_rhyme']},
        ),
        migrations.AlterModelOptions(
            name='verse',
            options={'ordering': ['verse_length', 'verse_text']},
        ),
        migrations.RemoveField(
            model_name='assonantrhyme',
            name='amount_words',
        ),
        migrations.RemoveField(
            model_name='consonantrhyme',
            name='amount_words',
        ),
    ]
