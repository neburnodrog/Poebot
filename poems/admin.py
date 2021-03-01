from django.contrib import admin
from .models import Verse, AssonantRhyme, ConsonantRhyme, Word, User
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')


class AssonantAdmin(admin.ModelAdmin):
    list_display = ("id", "assonant_rhyme", "amount_words", "amount_verses", "modified_date")
    search_fields = ("assonant_rhyme",)
    ordering = ["-amount_words", "-amount_verses"]


class ConsonantAdmin(admin.ModelAdmin):
    list_display = ("id", "consonant_rhyme", "assonant_rhyme", "amount_words", "amount_verses", "modified_date")
    search_fields = ("consonant_rhyme",)
    ordering = ["-amount_words", "-amount_verses"]


class WordAdmin(admin.ModelAdmin):
    list_display = ("word_text", "amount_verses", "consonant_rhyme", "assonant_rhyme")
    search_fields = ("word_text",)
    ordering = ["-amount_verses"]


class VerseAdmin(admin.ModelAdmin):
    list_display = ('id', 'verse_text', 'verse_length', "last_word", "is_beg", "is_int", "is_end", "date_of_creation", "modified_date")
    search_fields = ("verse_text",)


admin.site.register(AssonantRhyme, AssonantAdmin)
admin.site.register(ConsonantRhyme, ConsonantAdmin)
admin.site.register(Word, WordAdmin)
admin.site.register(Verse, VerseAdmin)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
