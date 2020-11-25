from django.contrib import admin
from .models import Verse, AssonantRhyme, ConsonantRhyme, Word
# Register your models here.


class WordAdmin(admin.ModelAdmin):
    list_display = ('word_text',)
    search_fields = ("word_text",)


class VerseAdmin(admin.ModelAdmin):
    list_display = ('id', 'verse_text', 'verse_length', "date_of_creation", "modified_date")
    search_fields = ("verse_text",)


class AssonantAdmin(admin.ModelAdmin):
    list_display = ("id", "assonant_rhyme", "amount_words", "modified_date")
    search_fields = ("assonant_rhyme",)


class ConsonantAdmin(admin.ModelAdmin):
    list_display = ("id", "consonant_rhyme", "assonant_rhyme", "amount_words", "modified_date")
    search_fields = ("consonant_rhyme",)


admin.site.register(Verse, VerseAdmin)
admin.site.register(AssonantRhyme, AssonantAdmin)
admin.site.register(ConsonantRhyme, ConsonantAdmin)
admin.site.register(Word, WordAdmin)
