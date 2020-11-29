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
        return "".join(self.verse_text.split()[:-1])