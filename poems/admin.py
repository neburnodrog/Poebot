from django.contrib import admin
from .models import Verse
# Register your models here.


class VerseAdmin(admin.ModelAdmin):
    list_display = ('verse_text', 'verse_length', 'cons_rhy', 'asson_rhy')


admin.site.register(Verse, VerseAdmin)