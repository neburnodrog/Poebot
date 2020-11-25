from django.db import models


class AssonantRhyme(models.Model):
    assonant_rhyme = models.TextField(unique=True)
    amount_words = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-amount_words', "assonant_rhyme"]

    def __str__(self):
        return "Rhyme: '-{}'".format(self.assonant_rhyme)


class ConsonantRhyme(models.Model):
    consonant_rhyme = models.TextField(unique=True)
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE)
    amount_words = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-amount_words', "consonant_rhyme"]

    def __str__(self):
        return "Rhyme: '-{}'".format(self.consonant_rhyme)


class Word(models.Model):
    word_text = models.TextField(unique=True)
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE)
    consonant_rhyme = models.ForeignKey(ConsonantRhyme, on_delete=models.CASCADE)
    amount_verses = models.IntegerField(default=0)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word_text

    def save(self, *args, **kwargs):
        super().save(Word, *args, **kwargs)
        self.assonant_rhyme.amount_words += 1
        self.assonant_rhyme.save()
        self.consonant_rhyme.amount_words += 1
        self.consonant_rhyme.save()


class Verse(models.Model):
    verse_text = models.TextField()
    verse_cut = models.TextField(default="")
    verse_length = models.IntegerField()
    last_word = models.ManyToManyField(Word)
    is_beg = models.BooleanField()
    is_int = models.BooleanField()
    is_end = models.BooleanField()
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['verse_length', 'verse_length']

    def __str__(self):
        return self.verse_text

    def save(self, *args, **kwargs):
        super().save(Verse, *args, **kwargs)
        last_words = self.last_word.all()
        for word in last_words:
            word.amount_verses = len(word.verse_set.all())
