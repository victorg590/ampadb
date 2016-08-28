from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator
from contactboard.models import telfRegex
import re

# Veure http://www.interior.gob.es/web/servicios-al-ciudadano/dni/calculo-del-digito-de-control-del-nif-nie
def validate_dni(dni):
    LLETRES = {0: 'T', 1: 'R', 2: 'W', 3: 'A', 4: 'G', 5: 'M', 6: 'Y', 7: 'F',
        8: 'P', 9: 'D', 10: 'X', 11: 'B', 12: 'N', 13: 'J', 14: 'Z', 15: 'S',
        16: 'Q', 17: 'V', 18: 'H', 19: 'L', 20: 'C', 21: 'K', 22: 'E'}
    dni_regex = re.compile(r'''
        ([XYZ]|[0-9])              # X, Y, Z (NIE) o número
        [0-9]{7}
        [ABCDEFGHJKLMNPQRSTVWXYZ]  # Lletra de validació
        ''', re.X)
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
    if dni[-1] != LLETRES[num % 23]:
        raise ValidationError('No és un DNI vàlid (la lletra no és correcta): '
            '{} != {}'.format(dni[-1], LLETRES[num % 23]))

class InscripcioForm(forms.Form):
    dni_pare = forms.CharField(label="DNI del pare", max_length=9,
        help_text='DNI o NIE del pare (no es guardarà).',
        validators=[validate_dni])
    dni_mare = forms.CharField(label="DNI de la mare", max_length=9,
        help_text='DNI o NIE de la mare (no es guardarà).',
        validators=[validate_dni])
    iban = forms.CharField(label="IBAN", required=False, help_text="Núm. de "
        "compte (si cal) (no es guardarà)")
    nif_titular = forms.CharField(label="NIF del titular del compte",
        required=False, help_text="Necessari si cal l'IBAN (no es guardarà)")
    drets_imatge = forms.BooleanField(label="Drets d'imatge", required=False,
        help_text="Segons l’article 18.1 de la Constitució i regulat per la "
        "llei 5/1982, de 5 de maig, sobre el dret a l’honor, a la intimitat "
        "personal i familiar a la pròpia imatge, en el cas que "
        "<strong>NO VOLGUEU</strong> que el vostre fill/a aparegui en "
        "fotografies, CD’s o vídeos que es realitzin a les activitats "
        "extraescolars cal que marqueu aquesta casella.")
    observacions = forms.CharField(widget=forms.Textarea, required=False,
        help_text="En l’apartat d’observacions poseu qualsevol suggeriment que "
        "intentarem tenir en compte.")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('iban') and not cleaned_data.get('nif_titular'):
            raise ValidationError("S'ha d'introduïr el NIF del titular amb el"
                " compte.")
