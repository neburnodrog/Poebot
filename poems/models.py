from django.db import models


class AssonantRhyme(models.Model):
    assonant_rhyme = models.TextField(unique=True)
    verse_number = models.IntegerField(default=0)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Assonant Rhyme: '{}'".format(self.assonant_rhyme)


class ConsonantRhyme(models.Model):
    consonant_rhyme = models.TextField(unique=True)
    assonant_rhyme = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE)
    verse_number = models.IntegerField(default=0)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Consonant Rhyme: '{}'".format(self.consonant_rhyme)


class Verse(models.Model):
    verse_text = models.TextField()
    verse_length = models.IntegerField()
    last_word = models.TextField()
    is_beg = models.BooleanField()
    is_int = models.BooleanField()
    is_end = models.BooleanField()
    asson_rhy = models.ForeignKey(AssonantRhyme, on_delete=models.CASCADE)
    cons_rhy = models.ForeignKey(ConsonantRhyme, on_delete=models.CASCADE)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.verse_text + ", Consonant Rhyme: '{}', Assonant Rhyme: '{}'".format(self.cons_rhy.consonant_rhyme,
                                                                                        self.asson_rhy.assonant_rhyme)

    def save(self, *args, **kwargs):
        super(Verse, self).save(*args, **kwargs)
        asson_object = self.asson_rhy
        asson_object.verse_number = len(self.asson_rhy.verse_set.all())
        asson_object.save()

        cons_object = self.cons_rhy
        cons_object.verse_number = len(self.cons_rhy.verse_set.all())
        cons_object.save()
