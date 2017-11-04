import re
from ampadb.support import Forms
from django import forms
from django.core.exceptions import ValidationError
from .models import Extraescolar, Inscripcio


class _ExtraescolarMeta:  # pylint: disable=too-few-public-methods
    model = Extraescolar
    fields = [
        'nom', 'id_interna', 'descripcio_curta', 'descripcio',
        'inscripcio_des_de', 'inscripcio_fins_a', 'preu', 'cursos'
    ]


class ExtraescolarForms:  # pylint: disable=too-few-public-methods
    class AddForm(Forms.ModelForm):
        class Meta(_ExtraescolarMeta):
            pass

    class EditForm(Forms.ModelForm):
        class Meta(_ExtraescolarMeta):
            pass

        id_interna = forms.CharField(disabled=True, required=False)


# Veure http://www.interior.gob.es/web/servicios-al-ciudadano/dni/calculo-del-digito-de-control-del-nif-nie # pylint: disable=line-too-long
def validate_dni(dni):
    lletres = "TRWAGMYFPDXBNJZSQVHLCKE"
    dni_regex = re.compile(r'''
        ([XYZ]|[0-9])              # X, Y, Z (NIE) o número
        [0-9]{7}
        [ABCDEFGHJKLMNPQRSTVWXYZ]  # Lletra de validació
        ''', re.VERBOSE)
    if re.fullmatch(dni_regex, dni) is None:
        raise ValidationError('El format del DNI no és vàlid')
    # NIEs
    if dni[0].upper() == 'X':
        dni = '0' + dni[1:]
    elif dni[0].upper() == 'Y':
        dni = '1' + dni[1:]
    elif dni[0].upper() == 'Z':
        dni = '2' + dni[1:]
    num = int(dni[:-1])
    if dni[-1] != lletres[num % 23]:
        raise ValidationError('No és un DNI vàlid (la lletra no és correcta).')


class InscripcioForm(Forms.Form):
    dni_tutor_1 = forms.CharField(
        label="DNI del tutor 1",
        max_length=9,
        help_text='DNI o NIE del tutor 1 (no es guardarà).',
        validators=[validate_dni])
    dni_tutor_2 = forms.CharField(
        label="DNI del tutor 2",
        max_length=9,
        help_text='DNI o NIE del tutor 2 (no es guardarà).',
        validators=[validate_dni])
    catsalut = forms.CharField(label="Núm. targeta sanitària (Catsalut)")
    iban = forms.CharField(
        label="IBAN",
        required=False,
        help_text="Núm. de compte (si cal) (no es guardarà)")
    nif_titular = forms.CharField(
        label="NIF del titular del compte",
        required=False,
        help_text="Necessari si cal l'IBAN (no es guardarà)")
    drets_imatge = forms.BooleanField(
        label="Drets d'imatge",
        required=False,
        help_text=(
            "Segons l’article 18.1 de la Constitució i regulat per la "
            "llei 5/1982, de 5 de maig, sobre el dret a l’honor, a la "
            "intimitat personal i familiar a la pròpia imatge, en el cas que "
            "<strong>NO VOLGUEU</strong> que el vostre fill/a aparegui en "
            "fotografies, CD’s o vídeos que es realitzin a les activitats "
            "extraescolars cal que marqueu aquesta casella."))
    observacions = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="En l’apartat d’observacions poseu qualsevol suggeriment "
        "que intentarem tenir en compte.")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('iban') and not cleaned_data.get('nif_titular'):
            self.add_error(
                'nif_titular',
                ValidationError(
                    "S'ha d'introduïr el NIF del titular amb el compte."))


def validate_inscripcio_exists(pk_inscripcio):
    try:
        pk_inscripcio = int(pk_inscripcio)
    except ValueError:
        raise ValidationError('Clau invàlida: ' + pk_inscripcio)
    if not Inscripcio.objects.filter(pk=pk_inscripcio).exists():
        raise ValidationError('No existeix la inscripció ' +
                              str(pk_inscripcio))


class SearchInscripcioForm(Forms.Form):
    q = forms.CharField(  # pylint: disable=invalid-name
        label='Id inscripció',
        validators=[validate_inscripcio_exists])


class InscripcioAdminForm(Forms.ModelForm):
    class Meta:
        model = Inscripcio
        fields = ['confirmat', 'pagat']
