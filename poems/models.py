from django.db import models
from django.forms import ModelForm


# Create your models here.
class Verse(models.Model):
    verse_text = models.TextField()
    verse_length = models.IntegerField()
    cons_rhy = models.TextField()
    asson_rhy = models.TextField()
    last_word = models.TextField()
    is_beg = models.BooleanField()
    is_int = models.BooleanField()
    is_end = models.BooleanField()
