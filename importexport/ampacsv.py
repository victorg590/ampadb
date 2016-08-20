import csv

fieldnames = [
    'pk',
    'Nom',
    'Cognoms',
    'Data de naixement',
    'Correu alumne',
    'Correu pare',
    'Correu mare',
    'Teléfon pare',
    'Teléfon mare',
    'Compartir',
    'Classe',
    'Curs',
    'Usuari',
    'Eliminar'
]

class AmpaDialect(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\r\n'  # Per compatibilitat amb Windows
    skipinitialspace = True

def get_template(outfile):
    writer = csv.DictWriter(outfile, fieldnames)
    writer.writeheader()
