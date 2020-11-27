import os
import csv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poemautomator.settings")
django.setup()

from poems.models import AssonantRhyme, ConsonantRhyme, Verse, Word


file = open('verse_list.csv', 'r')
reader = csv.reader(file)

rows = list(reader)

length_rows = len(rows)

for i, row in enumerate(rows):
    print(f"[+] importing row to DB [{i}/{length_rows}]...")
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
        word_object = Word.objects.get(word_text=last_word)
    except Word.DoesNotExist:
        word_object = Word.objects.create(word_text=last_word,
                                          consonant_rhyme=consonant_rhyme_obj,
                                          assonant_rhyme=assonant_rhyme_obj,
                                          )

    try:
        verse_object = Verse.objects.get(verse_text=verse_text,
                                         )

    except Verse.DoesNotExist:
        verse_object = Verse.objects.create(verse_text=verse_text,
                                            verse_cut="".join(verse_text.split()[:-1]),
                                            verse_length=verse_length,
                                            is_beg=is_beg,
                                            is_int=is_int,
                                            is_end=is_end,
                                            )

        verse_object.last_word.add(word_object)
        verse_object.save()
