import csv

fieldnames = [
    'pk',
    'Nom',
    'Cognoms',
    'Data de naixement',
    'Correu alumne',
    'Compartir correu alumne',
    'Correu pare',
    'Compartir correu pare',
    'Correu mare',
    'Compartir correu mare',
    'Telèfon alumne',
    'Compartir telèfon alumne',
    'Telèfon pare',
    'Compartir telèfon pare',
    'Telèfon mare',
    'Compartir telèfon mare',
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
