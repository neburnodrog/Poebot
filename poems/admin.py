from django.contrib import admin
from .models import Verse, AssonantRhyme, ConsonantRhyme
# Register your models here.


class VerseAdmin(admin.ModelAdmin):
    list_display = ('verse_text', 'verse_length', 'cons_rhy', 'asson_rhy', "date_of_creation")


class AssonantAdmin(admin.ModelAdmin):
    list_display = ("assonant_rhyme", "verse_number")


class ConsonantAdmin(admin.ModelAdmin):
    list_display = ("consonant_rhyme", "assonant_rhyme", "verse_number")


admin.site.register(Verse, VerseAdmin)
admin.site.register(AssonantRhyme, AssonantAdmin)
admin.site.register(ConsonantRhyme, ConsonantAdmin)
