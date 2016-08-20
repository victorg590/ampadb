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
    format = forms.ChoiceField(required=False, choices=FORMAT_CHOICES,
        widget=forms.RadioSelect)
    ifile = forms.FileField(required=True, label="Arxiu d'importació")
