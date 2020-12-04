from django.db import models


class AssonantRhyme(models.Model):
    assonant_rhyme = models.TextField(unique=True)
    amount_words = models.IntegerField(default=0)
    amount_verses = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Rhyme: '{}'".format(self.assonant_rhyme)


class ConsonantRhyme(models.Model):
    consonant_rhyme = models.TextField(unique=True)
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE, default=1)
    amount_words = models.IntegerField(default=0)
    amount_verses = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Rhyme: '{}'".format(self.consonant_rhyme)


class Word(models.Model):
    word_text = models.TextField(unique=True)
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

    def is_beg_verses(self):
        return self.verse_set.filter(is_beg=True).count()

    def is_int_verses(self):
        return self.verse_set.filter(is_int=True).count()

    def is_end_verses(self):
        return self.verse_set.filter(is_end=True).count()

    def is_beg_end_verses(self):
        return self.verse_set.filter(is_beg=True, is_end=True)


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
        return " ".join(self.verse_text.split()[:-1])