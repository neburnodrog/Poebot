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
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE)
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

    def __str__(self):
        return self.word_text


class Verse(models.Model):
    verse_text = models.TextField()
    verse_cut = models.TextField(default="")
    verse_length = models.IntegerField()
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE, default=1)
    consonant_rhyme = models.ForeignKey(ConsonantRhyme, on_delete=models.CASCADE, default=1)
    last_word = models.ManyToManyField(Word)
    is_beg = models.BooleanField()
    is_int = models.BooleanField()
    is_end = models.BooleanField()
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.verse_text
