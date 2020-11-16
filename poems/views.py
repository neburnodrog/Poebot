from django.views.generic import ListView, FormView
from django.http import JsonResponse, HttpResponseRedirect
from .forms import CreatePoemForm
from .models import Verse
from .poemator import PoemAutomator
from django.shortcuts import render
from urllib.parse import urlencode
from django.urls import reverse_lazy


def home_view(request):
    return render(request, "poems/home.html")


# Create your views here.
class CreatePoemView(FormView):
    template_name = "poems/create-poem.html"
    form_class = CreatePoemForm

    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)
        if 'submit' in self.request.GET:
            form = CreatePoemForm(self.request.GET)
            if form.is_valid():
                query_string = urlencode(form.data, ascii)
                return HttpResponseRedirect(reverse_lazy("poems:poem") + "?" + query_string)
            return self.form_invalid(form)

        return render(self.request, self.get_template_names() , context=self.get_context_data())


def validate_rhyme(request):
    ver_len_value = request.GET.get("verse_length")
    rhy_seq = request.GET.get("rhy_seq")

    for key in request.GET:
        if key != "verse_length" and key != "rhy_seq":
            rhyme_value = request.GET.get(key)

            if key == key.upper():  # Key is UPPERCASE -> consonant_rhyme checker
                filtered_verses = Verse.objects.filter(cons_rhy__iexact=rhyme_value, verse_length=ver_len_value)

            else:  # Key is LOWERCASE -> assonant_rhyme checker
                filtered_verses = Verse.objects.filter(asson_rhy__iexact=rhyme_value, verse_length=ver_len_value)

            data = {
                "not_valid": len(filtered_verses) < 2 * rhy_seq.count(key)  # TODO -> Check if we can lower the value
            }

            if data["not_valid"]:
                data["error_message"] = "No hay rimas suficientes de este tipo en la base de datos para continuar.\n"

    return JsonResponse(data)


class PoemView(ListView):
    template_name = "poems/poem.html"

    def get_queryset(self):
        arguments = {}

        left_keys = dict(self.request.GET)

        ver_num = self.request.GET.get('ver_num')  # required
        arguments['ver_num'] = ver_num
        del left_keys['ver_num']

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

        return context
