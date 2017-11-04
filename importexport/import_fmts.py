import json
import pickle
import gzip
import pathlib
import tempfile
from io import BytesIO
from enum import Enum
from .pklf import CURRENT_VERSION, PickledInfo
from . import aesencrypt
from .ampacsv import InvalidFormat


class IEFormats(Enum):
    AUTO = ''
    CSV = 'csv'
    JSON = 'json'
    PICKLE = 'pickle'
    AMPACSV = 'csv.ampacsv'
    EXCELCSV = 'csv.excel'


def detect_format(filename):
    """Detecta un format a partir la extensió.

    Si no es pot detectar, envía un `ValueError`
    """
    path = pathlib.PurePath(filename)
    if len(path.suffixes) < 1:
        raise ValueError
    if path.suffixes[-1] == '.csv':
        return IEFormats.AMPACSV
    elif path.suffixes[-1] == '.json':
        return IEFormats.JSON
    elif path.suffixes[-2:] == ['.pkl', '.gz']:
        return IEFormats.PICKLE
    elif path.suffixes[-3:] == ['.pkl', '.gz', '.aes']:
        return IEFormats.PICKLE
    else:
        raise ValueError


def bytestream_to_text(bytestream, encoding='utf-8'):
    textstream = tempfile.TemporaryFile(mode='w+t')
    for chunk in bytestream.chunks():
        try:
            decoded_chunk = chunk.decode(encoding)
            textstream.write(decoded_chunk)
        except UnicodeDecodeError:
            raise InvalidFormat('Codificació incorrecte. Aquesta hauria de'
                                ' ser Unicode (UTF-8)')
    textstream.seek(0)
    return textstream


def import_json(infile, preexistents=''):
    try:
        info = PickledInfo.from_json(json.load(infile))
        info.unpickle(preexistents)
    except InvalidFormat:
        raise
    except Exception as ex:
        raise InvalidFormat("No és un arxiu JSON d'aquesta aplicació (" +
                            str(ex) + ')') from ex


def decrypt_pickle(infile, password):
    if infile.read(len(b'AMPAAES0')) != b'AMPAAES0':
        raise InvalidFormat('No està xifrat o no és un arxiu de'
                            'còpia de seguretat')
    init_vector = infile.read(aesencrypt.IV_LENGTH)
    plain_pickle = BytesIO()
    aesencrypt.decrypt(infile, plain_pickle,
                       aesencrypt.CryptoParams(password, init_vector))
    return plain_pickle


def import_pickle(infile, password, preexistents=''):
    if password:
        plain_pickle = decrypt_pickle(infile, password)
    else:
        plain_pickle = infile
    try:
        try:
            plain_pickle.seek(0)
            with gzip.GzipFile(fileobj=plain_pickle) as gzfile:
                return import_pickle_uncompressed(gzfile, password != '',
                                                  preexistents)
        except OSError:
            # Prova per si no està comprimit
            return import_pickle_uncompressed(infile, password != '',
                                              preexistents)
    except EOFError:
        raise InvalidFormat('Contrasenya incorrecta o no és un arxiu Pickle'
                            if password else 'No és un arxiu Pickle')


def import_pickle_uncompressed(infile, encrypted, preexistents=''):
    try:
        info = pickle.load(infile)
    except pickle.UnpicklingError:
        raise InvalidFormat('Contrasenya incorrecta o no és un arxiu Pickle'
                            if encrypted else 'No és un arxiu Pickle')
    try:
        info.check_version(CURRENT_VERSION)
        info.unpickle(preexistents)
    except InvalidFormat:
        raise
    except Exception as ex:
        raise InvalidFormat(
            "No és un arxiu Pickle d'aquesta aplicació ({})".format(
                ex)) from ex
