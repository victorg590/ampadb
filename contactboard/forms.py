from ampadb.support import Forms
from django import forms
from django.core.exceptions import ValidationError
from string import ascii_uppercase
from .models import Alumne, Classe, Curs, validate_non_reserved_id


def validate_classe_id_unique(value):
    if Classe.objects.filter(id_interna=value).exists():
        raise ValidationError('%(value)s already exists',
                              params={'value': value})


def validate_curs_id_unique(value):
    if Curs.objects.filter(id_interna=value).exists():
        raise ValidationError('%(value)s already exists',
                              params={'value': value})


class ClasseForms:
    class NewForm(Forms.Form):
        nom = forms.ChoiceField(
            required=True,
            choices=[(c, c) for c in ascii_uppercase])
        id_interna = forms.SlugField(
            max_length=20, required=True,
            validators=[validate_non_reserved_id, validate_classe_id_unique],
            help_text=(
                'Forma curta de referir-se a la classe. Ha de ser única i '
                '<em>no</em> es pot canviar més endavant.'))
        curs = forms.CharField(disabled=True, required=False)

    class EditForm(NewForm):
        id_interna = forms.SlugField(disabled=True, required=False)
        curs = forms.ModelChoiceField(
            queryset=Curs.objects.all(), required=True,
            to_field_name='id_interna', empty_label=None)


class CursForms:
    class NewForm(Forms.Form):
        nom = forms.CharField(max_length=50, required=True)
        id_interna = forms.SlugField(
            max_length=20, required=True,
            validators=[validate_curs_id_unique],
            help_text=(
                'Forma curta de referir-se al curs. Ha de ser única i'
                ' <em>no</em> es pot canviar més endavant.'))
        ordre = forms.IntegerField(
            required=False, min_value=0, max_value=32767,
            help_text=(
                'Ordre dels cursos. Ex.: 1er ESO = 1, 2on ESO = 2, ...,'
                ' 1er Batx = 5...'))

    class EditForm(Forms.Form):
        nom = forms.CharField(max_length=50, required=True)
        id_interna = forms.SlugField(disabled=True, required=False)
        ordre = forms.IntegerField(
            required=False, min_value=0, max_value=32767,
            help_text=(
                'Ordre dels cursos. Ex.: 1er ESO = 1, 2on ESO = 2, ...,'
                ' 1er Batx = 5...'))


class _AlumneMeta:
    model = Alumne
    fields = [
        'nom', 'cognoms', 'classe', 'nom_tutor_1',
        'cognoms_tutor_1', 'nom_tutor_2', 'cognoms_tutor_2', 'correu_alumne',
        'compartir_correu_alumne', 'correu_tutor_1',
        'compartir_correu_tutor_1', 'correu_tutor_2',
        'compartir_correu_tutor_2', 'telefon_alumne',
        'compartir_telefon_alumne', 'telefon_tutor_1',
        'compartir_telefon_tutor_1', 'telefon_tutor_2',
        'compartir_telefon_tutor_2'
    ]


class AlumneForms:
    class NewForm(Forms.ModelForm):
        class Meta(_AlumneMeta):
            exclude = ['classe']

    class EditForm(Forms.ModelForm):
        class Meta(_AlumneMeta):
            exclude = ['classe']
        nom = forms.CharField(disabled=True, required=False)
        cognoms = forms.CharField(disabled=True, required=False)

        def clean(self):
            cleaned_data = super().clean()
            if not any(map(cleaned_data.get, ['correu_alumne',
                                              'correu_tutor_2',
                                              'correu_tutor_1'])):
                raise ValidationError("Es requereix un correu com a mínim.")

    class AdminEditForm(Forms.ModelForm):
        class Meta(_AlumneMeta):
            pass


class MailtoForm(Forms.Form):
    TO_ALUMNES = 'alumnes'
    TO_TUTORS = 'tutors'
    TO = [
        (TO_ALUMNES, 'Alumnes'),
        (TO_TUTORS, 'Tutors')
    ]
    AS_TO = 'no'
    AS_BCC = ''
    SEND_MODE = [
        (AS_TO, 'Per a'),
        (AS_BCC, 'Cco')
    ]
    enviar_a = forms.MultipleChoiceField(choices=TO,
                                         widget=forms.CheckboxSelectMultiple)
    enviar_com = forms.ChoiceField(
        choices=SEND_MODE, required=False,
        widget=forms.RadioSelect, help_text=(
            "Per privacitat, els correus s'envien amb còpia oculta. Canvia-ho "
            "aqui per enviar com a destinataris (\"Per a\"). Aixó permet que "
            "tothom vegi la resta d'adresses"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classes'] = forms.MultipleChoiceField(choices=[
            (classe.id_interna, str(classe))
            for classe in Classe.objects.all()])


class MailtoClasseForm(MailtoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del(self.fields['classes'])
