from django import forms
from django.core.exceptions import ValidationError
from poems.help_funcs import sequence_without_spaces


class CreatePoemForm(forms.Form):

    ver_num = forms.IntegerField(help_text="Aquí el número de versos que quieres que tenga tu poema.",
                              label="Número de versos",)

    verse_length = forms.IntegerField(help_text="Aquí la longitud que quieres que tengan los versos (en número de sílabas).",
                                      label="Longitud de los versos",
                                      required=False,
                                      min_value=5,
                                      max_value=19,)

    rhy_seq = forms.CharField(help_text="Aquí la secuencia de las rimas. Letras mayúsculas implican rima consonante, minúsculas asonante.",
                              label="Secuencia de rimas",
                              required=False)

    select_verses = forms.ChoiceField(label="Quieres elegir las rimas? ",
                                      choices=[('no', 'No'), ('yes', 'Sí')],
                                      required=False,
                                      widget=forms.widgets.Select)

    def __init__(self, *args, **kwargs):
        super(CreatePoemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.name == "select_verses":
                visible.field.widget.attrs['style'] = 'display:none;'

    def clean_verse_length(self):
        data = self.cleaned_data.get("verse_length")
        if not data:
            return False
        return data

    def clean_rhy_seq(self):
        data = self.cleaned_data.get("rhy_seq")
        if not data:
            return False

        rhy_seq_data = self.cleaned_data.get("rhy_seq")
        num_ver_data = self.cleaned_data.get("ver_num")

        trimmed_rhy_seq = sequence_without_spaces(rhy_seq_data)

        if num_ver_data:
            if len(trimmed_rhy_seq) != num_ver_data:
                raise ValidationError(
                    "La secuencia de rimas ha de tener exactamente el mismo número de caracteres que número de versos (sin contar espacios)")

        return data
