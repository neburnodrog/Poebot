from django.contrib import admin
from .models import Verse, AssonantRhyme, ConsonantRhyme
# Register your models here.


class VerseAdmin(admin.ModelAdmin):
    list_display = ('id', 'verse_text', 'verse_length', 'cons_rhy', 'asson_rhy', "date_of_creation", "modified_date")
    search_fields = ("verse_text",)


class AssonantAdmin(admin.ModelAdmin):
    list_display = ("id", "assonant_rhyme", "verse_number", "modified_date")
    search_fields = ("assonant_rhyme",)


class ConsonantAdmin(admin.ModelAdmin):
    list_display = ("id", "consonant_rhyme", "assonant_rhyme", "verse_number", "modified_date")
    search_fields = ("consonant_rhyme",)


admin.site.register(Verse, VerseAdmin)
admin.site.register(AssonantRhyme, AssonantAdmin)
admin.site.register(ConsonantRhyme, ConsonantAdmin)
