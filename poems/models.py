import random
from django.db import models


class Verse(models.Model):
    verse_text = models.TextField()
    verse_length = models.IntegerField()
    cons_rhy = models.TextField()
    asson_rhy = models.TextField()
    last_word = models.TextField()
    is_beg = models.BooleanField()
    is_int = models.BooleanField()
    is_end = models.BooleanField()


def fetch_verses(**kwargs):
    """Retrieves a filtered list of verses from the DB"""
    if "unique" in kwargs and kwargs["unique"]:
        del kwargs["unique"]
        verses_list = Verse.objects.filter(**kwargs)

        # Only unique last_words
        unique_word_verses_list = []

        possible_last_words = set([verse.last_word for verse in verses_list])
        for word in possible_last_words:
            verse = random.choice([option for option in verses_list if option.last_word == word])
            unique_word_verses_list.append(verse)

        return unique_word_verses_list

    verses_list = Verse.objects.filter(**kwargs)
    return verses_list


def fetch_rhyme(long, limit = 0, cons = False):
    if isinstance(long, list):
        verses = Verse.objects.filter(verse_length__gte=long[0]).filter(verse_length__lte=long[1])
    else:
        verses = Verse.objects.filter(verse_length=long)

    if cons:
        verses = Verse.objects.values('cons_rhy').annotate(entries_count=models.Count('cons_rhy'))
        verses = [verse for verse in verses if verse["entries_count"] > limit]
        verse = random.choice(verses)
        return verse["cons_rhy"]

    elif not cons:
        verses = Verse.objects.values('asson_rhy').annotate(entries_count=models.Count('asson_rhy'))
        verses = [verse for verse in verses if verse["entries_count"] > limit]
        verse = random.choice(verses)
        return verse["asson_rhy"]
