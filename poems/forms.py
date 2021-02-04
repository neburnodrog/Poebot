from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from poemautomator.settings import DEFAULT_FROM_EMAIL
from django.template.loader import render_to_string
from django.core.mail import send_mail


class CreatePoemForm(forms.Form):

    ver_num = forms.IntegerField(
        label="Número de versos",
        help_text="Min: 1, Max: 20",
        required=False,
        min_value=1,
        max_value=20,
    )

    verse_length = forms.IntegerField(
        label="Longitud de los versos",
        help_text="Min: 5, Max: 14",
        required=False,
        min_value=5,
        max_value=14,
    )

    rhy_seq = forms.CharField(
        help_text="Ejemplo: ABBA ABBA",
        label="Secuencia de rimas",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control text-center"


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.visible_fields()

        username = fields[0]
        username.label = "Nombre de usuario"
        username.help_text = (
            "150 caracteres máximo. Sólo letras , dígitos y @ . - + o _"
        )
        username.field.widget.attrs["class"] = "form-control text-center"

        email = fields[1]
        email.field.widget.attrs["required"] = "true"
        email.label = "Dirección de correo electrónico"
        email.help_text = "introduce aquí tu e-mail."
        email.field.widget.attrs["class"] = "form-control text-center"

        password = fields[2]
        password.label = "Contraseña"
        password.help_text = "La contraseña no puede ser similar a tu otra información,\
        ha de contener al menos 8 caracteres y no podrá exclusivamente numérica."
        password.field.widget.attrs["class"] = "form-control text-center"

        password2 = fields[3]
        password2.label = "Confirmación de contraseña"
        password2.field.widget.attrs["class"] = "form-control text-center"
        password2.help_text = "Introduce la misma contraseña que antes para verificar."

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya existe")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está siendo usado")

        return email

    def save(self, request, *args, **kwargs):
        user = super().save(*args, commit=False, **kwargs)
        user.is_active = False
        user.save()
        to_email = user.email

        context = {
            "request": request,
            "protocol": request.scheme,
            "username": user.username,
            "domain": request.META["HTTP_HOST"],
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        }

        subject = render_to_string("email/activation_subject.txt", context)
        email = render_to_string("email/activation_body.txt", context)

        send_mail(subject, email, DEFAULT_FROM_EMAIL, [to_email])

        return user


class SignUpForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control text-center"
