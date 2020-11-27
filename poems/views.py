from urllib.parse import urlencode
from typing import Union, Optional, List, Tuple, Dict, Any

from django.views.generic import ListView, FormView
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from .forms import CreatePoemForm
from .models import Verse, AssonantRhyme, ConsonantRhyme
from .poemator import PoemAutomator
from .analyse_verses import Syllabifier


def home_view(request):
    return render(request, "poems/home.html")


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

        return render(self.request, self.get_template_names(), context=self.get_context_data())


def validate_rhyme(request):
    data = request.GET
    for key in data:
        if key == "verse_length":
            ver_len_value = request.GET.get(key)
        elif key == "rhy_seq":
            rhy_seq = request.GET.get(key)
        else:
            rhyme_code = key
            rhyme_value = request.GET.get(rhyme_code)

    if rhyme_value == rhyme_value.upper():  # Key is UPPERCASE -> consonant_rhyme checker
        rhyme_value = Syllabifier(rhyme_value).consonant_rhyme  # This to be able to input either a word & an ending

        try:
            filtered_verses = Verse.objects.filter(cons_rhy=ConsonantRhyme.objects.get(consonant_rhyme=rhyme_value),
                                                   verse_length=ver_len_value)
        except ConsonantRhyme.DoesNotExist:
            filtered_verses = []

    else:  # Key is LOWERCASE -> assonant_rhyme checker
        rhyme_value = Syllabifier(rhyme_value).assonant_rhyme

        try:
            filtered_verses = Verse.objects.filter(asson_rhy=AssonantRhyme.objects.get(assonant_rhyme=rhyme_value),
                                                   verse_length=ver_len_value)

        except AssonantRhyme.DoesNotExist:
            filtered_verses = []

    data = {
        "not_valid": len(filtered_verses) < 2 * rhy_seq.count(rhyme_code)  # TODO -> Check if we can lower the value
    }

    if data["not_valid"]:
        data["error_message"] = "No hay rimas suficientes de este tipo en la base de datos para continuar."

    return JsonResponse(data)


class PoemView(ListView):
    template_name = "poems/poem.html"

    def get_queryset(self):
        arguments = {}
        rhymes_dict = {}

        for key in self.request.GET:
            if key in ["submit", "select_verses"]:
                continue
            elif key in ["ver_num", "verse_length", "rhy_seq"]:
                value = self.request.GET.get(key)
                arguments[key] = value
            else:
                rhymes_dict[key] = self.request.GET.get(key)

        if rhymes_dict:
            arguments["rhymes_to_use"] = rhymes_dict

        automator = PoemAutomator(**arguments)
        automator.control_branches()
        list_of_verses = automator.poem_generator()

        return list_of_verses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO ->  remember this to add functionality.

        return context
