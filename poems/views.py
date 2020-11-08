from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Verse
from django.db.models.query import QuerySet


# Create your views here.
class IndexView(TemplateView):
    template_name = "poems/index.html"
    all_fields = Verse._meta.get_fields()
    extra_context = {"fields": all_fields}


class VerseView(ListView):
    template_name = "poems/poem.html"
    paginate_by = 50

    def get_queryset(self):
        arguments = {}
        if self.request.GET.get('verse_length'):
            length_val = self.request.GET.get('verse_length')
            arguments['verse_length'] = length_val
        if self.request.GET.get('cons_rhy'):
            cons_val = self.request.GET.get('cons_rhy')
            arguments["cons_rhy"] = cons_val
        if self.request.GET.get('asson_rhy'):
            asson_val = self.request.GET.get('asson_rhy')
            arguments["asson_rhy"] = asson_val
        if self.request.GET.get('last_word'):
            last_word_val = self.request.GET.get('last_word')
            arguments["last_word"] = last_word_val
        if self.request.GET.get('verse_type'):
            verse_type_val = self.request.GET.get('verse_type')
            if verse_type_val == "is_beg":
                arguments["is_beg"] = True
            elif verse_type_val == "is_int":
                arguments["is_int"] = True
            else:
                arguments["is_end"] = True

        new_context = Verse.objects.filter(**arguments)
        return new_context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verse_length'] = self.request.GET.get('verse_length', '0')
        context['cons_rhy'] = self.request.GET.get('cons_rhy', "")
        context['asson_rhy'] = self.request.GET.get('asson_rhy', "")
        context['last_word'] = self.request.GET.get('last_word', "")
        context['verse_type'] = self.request.GET.get('verse_type', False)

        return context