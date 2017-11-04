from ampadb.support import Forms
from django import forms
from django.core.exceptions import ValidationError
from . import ies_format
from .ampacsv import InvalidFormat
from .import_fmts import IEFormats


class ExportForm(Forms.Form):
    FORMAT_CHOICES = [(IEFormats.CSV, 'CSV (E-mail)'), (IEFormats.AMPACSV,
                                                        'CSV (Importació)'),
                      (IEFormats.JSON, 'JSON'), (IEFormats.PICKLE, 'Pickle')]
    format = forms.ChoiceField(
        required=True, choices=FORMAT_CHOICES, widget=forms.RadioSelect)
    classe = forms.CharField(required=False, widget=forms.HiddenInput)
    contrasenya = forms.CharField(required=False, widget=forms.PasswordInput)
    repeteix_la_contrasenya = forms.CharField(
        required=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        contrasenya = cleaned_data.get('contrasenya')
        if contrasenya and (contrasenya !=
                            cleaned_data.get('repeteix_la_contrasenya')):
            self.add_error('repeteix_la_contrasenya',
                           ValidationError('La contrasenya no coincideix'))


class ImportForm(Forms.Form):
    FORMAT_CHOICES = [(IEFormats.AUTO, 'Autodetectar'),
                      (IEFormats.AMPACSV, 'CSV'), (IEFormats.EXCELCSV,
                                                   'CSV (Excel)'),
                      (IEFormats.JSON, 'JSON'), (IEFormats.PICKLE, 'Pickle')]
    PREEXISTENT_CHOICES = [('', 'Conservar'), ('DEL',
                                               'Eliminar no mencionades'),
                           ('DEL_ALL', 'Eliminar tot (no recomanat)')]
    format = forms.ChoiceField(
        required=False, choices=FORMAT_CHOICES, widget=forms.RadioSelect)
    contrasenya = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text=("Si és un arxiu Pickle xifrat, s'intentarà desxifrar amb"
                   " aquesta contrasenya. Si el format no és Pickle,"
                   " aquest camp s'ignorarà."))
    preexistents = forms.ChoiceField(
        required=False,  # 'Conservar' per defecte
        choices=PREEXISTENT_CHOICES,
        label='Entrades preexistents',
        widget=forms.RadioSelect,
        help_text=(
            "Què fer amb les entrades preexistents que no es mencionen a "
            "l'arxiu. \"Conservar\" no les modifica; \"Eliminar no "
            "mencionades\" les elimina, però, si la entrada existeix i conté "
            "dades que l'arxiu no té, aquestes es conserven (ex. si un alumne "
            "té el correu de l'alumne però l'arxiu no té aquest camp, es "
            "conserva el que ja tenia); \"Eliminar tot\" només deixa les "
            "dades que hi ha a l'arxiu."))
    ifile = forms.FileField(required=True, label="Arxiu d'importació")


class Ies:  # pylint: disable=too-few-public-methods
    class UploadForm(Forms.Form):
        ifile = forms.FileField(required=True, label="Arxiu d'importació")

        def clean(self):
            self.clean_file()

        def clean_file(self):
            ifile = self.cleaned_data['ifile']
            try:
                ies_format.validate(ifile)
            except InvalidFormat as ex:
                raise ValidationError(ex)
