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
        help_text="Mayúsculas: rima consonante. Minúsculas: asonante. <br>Espacio(s) en blanco: verso en blanco. Ejemplo: ABBA ABBA",
        label="Secuencia de rimas",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(CreatePoemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible == "ver_num":
                visible.field.widget.attrs['onkeydown'] = "return event.keyCode !== 69"
