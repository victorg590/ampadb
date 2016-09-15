from django import forms

class IEFormats:
    AUTO = ''
    CSV = 'csv'
    JSON = 'json'
    PICKLE = 'pickle'
    AMPACSV = 'csv.ampacsv'
    EXCELCSV = 'csv.excel'

class ExportForm(forms.Form):
    FORMAT_CHOICES = [
        (IEFormats.CSV, 'CSV (E-mail)'),
        (IEFormats.AMPACSV, 'CSV (Importació)'),
        (IEFormats.JSON, 'JSON'),
        (IEFormats.PICKLE, 'Pickle')
    ]
    format = forms.ChoiceField(required=True, choices=FORMAT_CHOICES,
        widget=forms.RadioSelect)
    classe = forms.CharField(required=False, widget=forms.HiddenInput)

class ImportForm(forms.Form):
    FORMAT_CHOICES = [
        (IEFormats.AUTO, 'Autodetectar'),
        (IEFormats.AMPACSV, 'CSV'),
        (IEFormats.EXCELCSV, 'CSV (Excel)'),
        (IEFormats.JSON, 'JSON'),
        (IEFormats.PICKLE, 'Pickle')
    ]
    PREEXISTENT_CHOICES = [
        ('', 'Conservar'),
        ('DEL', 'Eliminar no mencionades'),
        ('DEL_ALL', 'Eliminar tot (no recomanat)')
    ]
    format = forms.ChoiceField(required=False, choices=FORMAT_CHOICES,
        widget=forms.RadioSelect)
    preexistents = forms.ChoiceField(required=True,
        choices=PREEXISTENT_CHOICES, label='Entrades preexistents',
        widget=forms.RadioSelect, help_text="Què fer amb les entrades "
            "preexistents que no es mencionen a l'arxiu. \"Conservar\" no les "
            "modifica; \"Eliminar no mencionades\" les elimina, però, si la "
            "entrada existeix i conté dades que l'arxiu no té, aquestes es "
            "conserven (ex. si un alumne té el correu de l'alumne però l'arxiu "
            "no té aquest camp, es conversa el que ja tenia); \"Eliminar tot\" "
            "només deixa les dades que hi ha a l'arxiu.")
    ifile = forms.FileField(required=True, label="Arxiu d'importació")
