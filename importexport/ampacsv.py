import csv

FIELDNAMES = [
    'pk',
    'Nom',
    'Cognoms',
    'Nom tutor 1',
    'Cognoms tutor 1',
    'Nom tutor 2',
    'Cognoms tutor 2',
    'Correu alumne',
    'Compartir correu alumne',
    'Correu tutor 1',
    'Compartir correu tutor 1',
    'Correu tutor 2',
    'Compartir correu tutor 2',
    'Telèfon alumne',
    'Compartir telèfon alumne',
    'Telèfon tutor 1',
    'Compartir telèfon tutor 1',
    'Telèfon tutor 2',
    'Compartir telèfon tutor 2',
    'Classe',
    'Curs',
    'Usuari',
    'Eliminar'
]


class AmpaDialect(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    escapechar = '\\'
    doublequote = False
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\r\n'  # Per compatibilitat amb Windows
    skipinitialspace = True


def get_template(outfile):
    writer = csv.DictWriter(outfile, FIELDNAMES)
    writer.writeheader()
