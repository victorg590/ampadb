from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Alumne, Classe, Curs, validate_non_reserved_id, telfRegex

def validate_classe_id_unique(value):
    if Classe.objects.filter(id_interna=value).exists():
        raise ValidationError('%(value)s already exists',
            params={'value': value})

def validate_curs_id_unique(value):
    if Curs.objects.filter(id_interna=value).exists():
        raise ValidationError('%(value)s already exists',
            params={'value': value})

class ClasseForms:
    class NewForm(forms.Form):
        nom = forms.CharField(max_length=50, required=True)
        id_interna = forms.SlugField(max_length=20, required=True,
            validators=[validate_non_reserved_id, validate_classe_id_unique],
            help_text='Forma curta de referir-se a la classe. Ha de ser única i'
            ' <em>no</em> es pot canviar més endavant.')
        curs = forms.CharField(disabled=True, required=False)

    class EditForm(NewForm):
        id_interna = forms.SlugField(disabled=True, required=False)
        curs = forms.ModelChoiceField(queryset=Curs.objects.all(),
            required=True, to_field_name='id_interna', empty_label=None)

class CursForms:
    class NewForm(forms.Form):
        nom = forms.CharField(max_length=50, required=True)
        id_interna = forms.SlugField(max_length=20, required=True,
            validators=[validate_curs_id_unique],
            help_text='Forma curta de referir-se al curs. Ha de ser única i'
            ' <em>no</em> es pot canviar més endavant.')
        ordre = forms.IntegerField(required=False, min_value=0, max_value=32767,
            help_text='Ordre dels cursos. Ex.: 1er ESO = 1, 2on ESO = 2, ...,'
            ' 1er Batx = 5...')
    class EditForm(forms.Form):
        nom = forms.CharField(max_length=50, required=True)
        id_interna = forms.SlugField(disabled=True, required=False)
        ordre = forms.IntegerField(required=False, min_value=0, max_value=32767,
            help_text='Ordre dels cursos. Ex.: 1er ESO = 1, 2on ESO = 2, ...,'
            ' 1er Batx = 5...')

# class AlumneForms:
#     class NewForm(forms.Form):
#         nom = forms.CharField(max_length=255, required=True)
#         cognoms = forms.CharField(max_length=255, required=True)
#         classe = forms.CharField(disabled=True, required=False)
#         data_de_naixement = forms.DateField(required=True,
#             widget=forms.DateInput(format='%d/%m/%Y'),
#             input_formats=[
#                 '%d/%m/%Y',
#                 '%d-%m-%Y',
#                 '%d-%m-%y',
#                 '%d/%m/%y',
#                 '%Y-%m-%d'  # ISO
#             ]
#         )
#         correu_alumne = forms.EmailField(required=False)
#         correu_pare = forms.EmailField(required=False)
#         telefon_pare = forms.CharField(required=False, max_length=15,
#             validators=[RegexValidator(telfRegex)],
#             label='Telèfon pare')
#         correu_mare = forms.EmailField(required=False)
#         telefon_mare = forms.CharField(required=False, max_length=15,
#             validators=[RegexValidator(telfRegex)],
#             label='Telèfon mare')
#         compartir = forms.BooleanField(required=False, initial=False,
#             help_text='Si es selecciona, la classe podrà veure els correus i'
#             ' els telèfons')
#
#     class AdminEditForm(NewForm):
#         classe = forms.ModelChoiceField(required=True,
#             to_field_name='id_interna',
#             queryset=Classe.objects.all().order_by('curs'))
#
#     class EditForm(NewForm):
#         nom = forms.CharField(disabled=True, required=False)
#         cognoms = forms.CharField(disabled=True, required=False)
#         classe = forms.CharField(disabled=True, required=False)
#         data_de_naixement = forms.DateField(disabled=True, required=False,
#             widget=forms.DateInput(format='%d/%m/%Y'))

class _AlumneMeta:
    model = Alumne
    fields = ['nom', 'cognoms', 'classe', 'data_de_naixement',
        'correu_alumne', 'compartir_correu_alumne', 'correu_pare',
        'compartir_correu_pare', 'correu_mare', 'compartir_correu_mare',
        'telefon_alumne', 'compartir_telefon_alumne', 'telefon_pare',
        'compartir_telefon_pare', 'telefon_mare',
        'compartir_telefon_mare']

class AlumneForms:
    class NewForm(forms.ModelForm):
        class Meta(_AlumneMeta):
            pass
        classe = forms.CharField(disabled=True, required=False)
        data_de_naixement = forms.DateField(required=True,
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=[
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%d-%m-%y',
                '%d/%m/%y',
                '%Y-%m-%d'  # ISO
            ]
        )

    class EditForm(forms.ModelForm):
        class Meta(_AlumneMeta):
            pass
        nom = forms.CharField(disabled=True, required=False)
        cognoms = forms.CharField(disabled=True, required=False)
        data_de_naixement = forms.DateField(disabled=True, required=False,
            widget=forms.DateInput(format='%d/%m/%Y'))

    class AdminEditForm(forms.ModelForm):
        class Meta(_AlumneMeta):
            pass

class MailtoForm(forms.Form):
    TO_ALUMNES = 'alumnes'
    TO_PARES = 'pares'
    TO_MARES = 'mares'
    TO = [
        (TO_ALUMNES, 'Alumnes'),
        (TO_PARES, 'Pares'),
        (TO_MARES, 'Mares')
    ]
    AS_TO = 'no'
    AS_BCC = ''
    SEND_MODE = [
        (AS_TO, 'Per a'),
        (AS_BCC, 'Cco')
    ]
    enviar_a = forms.MultipleChoiceField(choices=TO,
        widget=forms.CheckboxSelectMultiple)
    enviar_com = forms.ChoiceField(choices=SEND_MODE, required=False,
        widget=forms.RadioSelect, help_text='Per privacitat, els correus'
        " s'envien amb còpia oculta. Canvia-ho aqui per enviar com a"
        ' destinataris ("Per a"). Aixó permet que tothom vegi la resta'
        " d'adresses")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classes'] = forms.MultipleChoiceField(choices=[
            (classe.id_interna, str(classe))
            for classe in Classe.objects.all()])

class MailtoClasseForm(MailtoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del(self.fields['classes'])
