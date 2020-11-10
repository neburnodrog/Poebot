from django.views.generic import ListView, FormView
from .forms import CreatePoemForm
from .models import Verse
from .poemator import PoemAutomator


# Create your views here.
class IndexView(FormView):
    template_name = "poems/create-poem.html"
    form_class = CreatePoemForm


class VerseView(ListView):
    template_name = "poems/poem.html"
    paginate_by = 50

    def get_queryset(self):
        arguments = {}

        left_keys = dict(self.request.GET)

        if self.request.GET.get('verse_num'):
            num_ver = self.request.GET.get('verse_num')
            arguments['verse_num'] = num_ver
            del left_keys['verse_num']

        if self.request.GET.get('verse_length'):
            lon_ver = self.request.GET.get('verse_length')
            arguments["verse_length"] = lon_ver
            del left_keys['verse_length']

        if self.request.GET.get('rhy_seq'):
            rhy_seq = self.request.GET.get('rhy_seq')
            arguments["rhy_seq"] = rhy_seq
            del left_keys['rhy_seq']

        if self.request.GET.get('select_verses') == "yes":
            arguments["select_verses"] = True
            del left_keys['select_verses']

            for key in left_keys.keys():
                value = self.request.GET.get(key)
                arguments[key] = value

            automator = PoemAutomator(**arguments)
            automator.user_determined_rhymes()
            list_of_verses = automator.poem_generator()

        else:
            automator = PoemAutomator(**arguments)
            automator.random_rhymes()
            list_of_verses = automator.poem_generator()

        return list_of_verses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verse_length'] = self.request.GET.get('verse_length', '0')
        context['cons_rhy'] = self.request.GET.get('cons_rhy', "")
        context['asson_rhy'] = self.request.GET.get('asson_rhy', "")
        context['last_word'] = self.request.GET.get('last_word', "")
        context['verse_type'] = self.request.GET.get('verse_type', False)

        return context
