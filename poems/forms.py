from django import forms
from django.core.exceptions import ValidationError
from poems.help_funcs import sequence_without_spaces


class CreatePoemForm(forms.Form):

    ver_num = forms.IntegerField(
        help_text="Número de versos que tendrá el poema generado.",
        label="Número de versos",
    )

    verse_length = forms.IntegerField(
        help_text="Longitud de los versos generados (medidos en número de sílabas).",
        label="Longitud de los versos",
        required=False,
        min_value=5,
        max_value=19,
    )

    rhy_seq = forms.CharField(
        help_text="Mayúsculas: rima consonante. Minúsculas: asonante. Espacio(s) en blanco: verso en blanco. Ejemplo: ABBA ABBA",
        label="Secuencia de rimas",
        required=False
    )

    select_verses = forms.ChoiceField(
        label="Quieres elegir las rimas? ",
        choices=[('no', 'No'), ('yes', 'Sí')],
        required=False,
        widget=forms.widgets.Select
    )

    def __init__(self, *args, **kwargs):
        super(CreatePoemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.name == "select_verses":
                visible.field.widget.attrs['style'] = 'display:none;'
