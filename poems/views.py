# IMPORTS
from urllib.parse import urlencode
from pyverse import Pyverse
import random

from django.forms.forms import BaseForm
from django.views.generic import ListView, FormView, TemplateView, DetailView
from django.http import JsonResponse, HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from .forms import CreatePoemForm, RegisterForm
from .models import Verse, AssonantRhyme, ConsonantRhyme
from .poemator import PoemAutomator


# Views
class HomeView(TemplateView):
    template_name = "poems/home.html"


class CreatePoemView(FormView):
    template_name = "poems/create-poem.html"
    form_class = CreatePoemForm

    def get(self, *args, **kwargs) -> HttpResponse:
        super().get(*args, **kwargs)
        if self.request.GET:
            form = CreatePoemForm(self.request.GET)
            if form.is_valid():
                query_string = urlencode(form.data, ascii)
                return HttpResponseRedirect(
                    reverse_lazy("poems:poem") + "?" + query_string
                )
            return self.form_invalid(form)

        return render(
            self.request,
            self.get_template_names(),
            context=self.get_context_data()
        )


def validate_rhyme(request: HttpRequest) -> JsonResponse:
    data = request.GET

    for key in data:
        if key == "verse_length":
            ver_len_value: str = request.GET.get(key)
        elif key == "rhy_seq":
            rhy_seq_value: str = request.GET.get(key)
        else:
            rhyme_code: str = key
            rhyme_val: str = request.GET.get(rhyme_code).lower()

    # Key is UPPERCASE -> consonant_rhyme checker
    if rhyme_code == rhyme_code.upper():
        if rhyme_val.startswith("-"):
            table = str.maketrans({k: v for k, v in zip("áéíóú", "aeiou")})
            rhyme_val = rhyme_val.translate(table).strip("-")

        else:
            # This to be able to input either a word & an ending
            rhyme_val = Pyverse(rhyme_val).consonant_rhyme

        try:
            cons_obj = ConsonantRhyme.objects.get(consonant_rhyme=rhyme_val)
        except ConsonantRhyme.DoesNotExist:
            err_msg = "Esta rima no existe en la base de datos por el momento."
            data_resp = {"not_valid": True,
                         "error_message": err_msg}

            return JsonResponse(data_resp)

        if ver_len_value:
            verses = cons_obj.verse_set.values_list(
                "last_word_id").filter(verse_length=ver_len_value)
        else:
            verses = cons_obj.verse_set.values_list("last_word_id")

        words_count = set(verses)

    # Key is LOWERCASE -> assonant_rhyme checker
    else:
        if rhyme_val.startswith("-"):
            table = str.maketrans(
                {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", })
            rhyme_val = rhyme_val.translate(table).strip("-")

        else:
            # This to be able to input either a word & an ending
            rhyme_val = Pyverse(rhyme_val).assonant_rhyme

        try:
            asson_obj = AssonantRhyme.objects.get(assonant_rhyme=rhyme_val)
        except AssonantRhyme.DoesNotExist:
            err_msg = "Esta rima no existe en la base de datos por el momento."
            data_resp = {
                "not_valid": True,
                "error_message": err_msg
            }
            return JsonResponse(data_resp)

        if ver_len_value:
            verses = asson_obj.verse_set.values_list(
                "last_word_id").filter(verse_length=ver_len_value)
        else:
            verses = asson_obj.verse_set.values_list("last_word_id")

        words_count = set(verses)
        word_limit = 3 * rhy_seq_value.count(rhyme_code)
        verse_limit = 3 * word_limit
    if (
            len(words_count) < word_limit
            or len(verses) < verse_limit
    ):
        error_message = "No hay rimas suficientes de este tipo\
        en la base de datos para continuar."
        data_resp = {"not_valid": True,
                     "error_message": error_message}

    else:
        data_resp = {"not_valid": False}

    return JsonResponse(data_resp)


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
        automator.poem_generator()
        list_of_verses = automator.poem

        return list_of_verses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO ->  remember this to add functionality.

        return context


def change_verse(request: HttpRequest) -> JsonResponse:
    verse_id = request.GET.get('id')
    # verse_last_word = Verse.objects.filter(id=verse_id).values_list("last_word__word_text")[0][0]
    values_dict = Verse.objects.filter(id=verse_id).values(
        "verse_length",
        "consonant_rhyme",
        "is_beg",
        "is_int",
        "is_end",
    )[0]

    if possible_verses := Verse.objects.values_list("id").filter(
            **values_dict).exclude(id=verse_id):
        new_id = random.choice(possible_verses)[0]
        data = Verse.objects.values("id", "verse_text").get(id=new_id)
    else:
        data = {"not_valid": True}

    return JsonResponse(data)



def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            HttpResponseRedirect(
                reverse_lazy("poems:login")
            )

    else:
        form = RegisterForm()

    return render(
        request, 
        template_name="registration/register.html",
        context={"form": form},
    )


def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if (user is not None and default_token_generator.check_token(user, token)):
        user.is_active = True
        user.save()
        messages.add_message(
            request, messages.INFO, 
            'Cuenta activada. Ya puedes logearte.'
        )
    else:
        messages.add_message(
            request, messages.INFO, 
            'El link ha expirado. Contacta al administrador para activarla.'
        )

    return HttpResponseRedirect(
        reverse_lazy("poems:login")
    )



class ProfileView(DetailView):
    model = User()
    template_name = "registration/profile.html"
