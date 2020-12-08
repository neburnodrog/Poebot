from django import forms
from django.core.exceptions import ValidationError
from poems.help_funcs import sequence_without_spaces


class CreatePoemForm(forms.Form):

    ver_num = forms.IntegerField(
        label="Número de versos",
        help_text="Número entero positivo.",
        required=False,
        max_value=20
    )

    verse_length = forms.IntegerField(
        help_text="Medidos en número de sílabas (Mínimo 5 y máximo 19).",
        label="Longitud de los versos",
        required=False,
        min_value=5,
        max_value=19,
    )

    rhy_seq = forms.CharField(
        help_text="Mayúsculas: rima consonante. Minúsculas: asonante. Espacio(s) en blanco: verso en blanco. Ejemplo: ABBA ABBA",
        label="Secuencia de rimas",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(CreatePoemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible == "ver_num":
                visible.field.widget.attrs['onkeydown'] = "return event.keyCode !== 69"
