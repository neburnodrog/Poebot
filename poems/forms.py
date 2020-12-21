from django import forms


class CreatePoemForm(forms.Form):

    ver_num = forms.IntegerField(
        label="Número de versos",
        help_text="Este campo requiere de un número entero positivo menor o igual a 20 para germinar.",
        required=False,
        min_value=1,
        max_value=20,
    )

    verse_length = forms.IntegerField(
        help_text="Medidos en número de sílabas (mínimo 5 y máximo 14).",
        label="Longitud de los versos",
        required=False,
        min_value=5,
        max_value=14,
    )

    rhy_seq = forms.CharField(
        help_text="Ejemplo: ABBA ABBA. Mayúsculas: rima consonante.<br>"
                  "Minúsculas: rima asonante. Espacio en blanco: verso en blanco.",
        label="Secuencia de rimas",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control text-center'
