from django import forms


class CreatePoemForm(forms.Form):

    ver_num = forms.CharField(help_text="Aquí el número de versos que quieres que tenga tu poema.",
                              label="Número de versos",)

    verse_length = forms.IntegerField(help_text="Aquí la longitud que quieres que tengan los versos (en número de sílabas).",
                                      label="Longitud de los versos",
                                      required=False,
                                      min_value=5,
                                      max_value=19)

    rhy_seq = forms.CharField(help_text="Aquí la secuencia de las rimas. Letras mayúsculas implican rima consonante, minúsculas asonante.",
                              label="Secuencia de rimas",
                              required=False)

    select_verses = forms.ChoiceField(label="Quieres elegir las rimas? ",
                                      choices=[('no', 'No'), ('yes', 'Sí')],
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(CreatePoemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.name == "select_verses":
                visible.field.widget.attrs['style'] = 'display:none;'

