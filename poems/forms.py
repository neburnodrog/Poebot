from django import forms


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
            visible.field.widget.attrs['class'] = 'form-control text-center'
