from django.db import models


class AssonantRhyme(models.Model):
    assonant_rhyme = models.CharField(unique=True, max_length=10)
    amount_words = models.IntegerField(default=0)
    amount_verses = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Rhyme: '{}'".format(self.assonant_rhyme)


class ConsonantRhyme(models.Model):
    consonant_rhyme = models.CharField(unique=True, max_length=20)
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE, default=1)
    amount_words = models.IntegerField(default=0)
    amount_verses = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Rhyme: '{}'".format(self.consonant_rhyme)


class Word(models.Model):
    word_text = models.CharField(max_length=50)
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE)
    consonant_rhyme = models.ForeignKey(ConsonantRhyme, on_delete=models.CASCADE)
    amount_verses = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    word_gender = models.CharField(max_length=15,
                                   choices=[("MASCULINE", "MASC"),
                                            ("FEMENINE", "FEM"),
                                            ("NONE", "X")],
                                   default="X")

    word_length = models.IntegerField(default=0)

    word_type = models.CharField(max_length=15,
                                 choices=[("ADJECTIVE", 'ADJ'),
                                          ("PREPOSITION", "ADP"),
                                          ("ADVERB", 'ADV'),
                                          ("VERB", 'VERB'),
                                          ("CONJUNCTION", 'CONJ'),
                                          ("DETERMINER", "DET"),
                                          ("NOUN", 'NOUN'),
                                          ("NUMERAL", "NUM"),
                                          ("PARTICLE", "PRT"),
                                          ("PRONOUN", "PRON"),
                                          ("OTHER", "X")],
                                 default="X")

    def __str__(self):
        return self.word_text


class Verse(models.Model):
    verse_text = models.TextField()
    verse_length = models.IntegerField()
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE)
    consonant_rhyme = models.ForeignKey(ConsonantRhyme, on_delete=models.CASCADE)
    last_word = models.ForeignKey(Word, on_delete=models.CASCADE)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_beg = models.BooleanField(default=False)
    is_int = models.BooleanField(default=False)
    is_end = models.BooleanField(default=False)

    def __str__(self):
        return self.verse_text

    def cut_verse(self):
        chopped_verse = self.verse_text.split()
        verse_cut, last_word = chopped_verse[:-1], chopped_verse[-1]
        return " ".join(verse_cut), last_word
