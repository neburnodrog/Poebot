import django
import os
import csv
from poems.models import AssonantRhyme, ConsonantRhyme, Verse


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poemautomator.settings")
django.setup()


file = open('verse_list.csv', 'r')
reader = csv.reader(file)

rows = list(reader)


for row in rows:
    assonant_rhyme = row[4]
    try:
        assonant_rhyme_obj = AssonantRhyme.objects.get(assonant_rhyme=assonant_rhyme)
    except AssonantRhyme.DoesNotExist:
        assonant_rhyme_obj = AssonantRhyme.objects.create(assonant_rhyme=assonant_rhyme)

    consonant_rhyme = row[3]
    try:
        consonant_rhyme_obj = ConsonantRhyme.objects.get(consonant_rhyme=consonant_rhyme)
    except ConsonantRhyme.DoesNotExist:
        consonant_rhyme_obj = ConsonantRhyme.objects.create(consonant_rhyme=consonant_rhyme,
                                                            assonant_rhyme=assonant_rhyme_obj)

    verse_text = row[1]
    verse_length = row[2]
    last_word = row[5]
    is_beg = row[6]
    is_int = row[7]
    is_end = row[8]

    try:
        verse_obj = Verse.objects.get(verse_text=verse_text, cons_rhy=consonant_rhyme_obj, asson_rhy=assonant_rhyme_obj)
    except Verse.DoesNotExist:
        verse_obj = Verse.objects.create(verse_text=verse_text,
                                         verse_length=verse_length,
                                         last_word=last_word,
                                         is_beg=is_beg,
                                         is_int=is_int,
                                         is_end=is_end,
                                         cons_rhy=consonant_rhyme_obj,
                                         asson_rhy=assonant_rhyme_obj,
                                         )

        verse_obj.save()
