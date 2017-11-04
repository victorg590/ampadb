import shlex
from django.db.models.query_utils import Q

_dummycomposer = lambda key, exact: Q()  # pylint: disable=invalid-name


def parse_token(token, composer):
    if '|' in token:
        first, *other = token.split('|')
        current = parse_token(first, composer)
        for tok in other:
            current |= parse_token(tok, composer)
        return current
    if token[0] == '"':
        return composer(token[1:-1], False)
    if token[0] == "'":
        return composer(token[1:-1], True)
    return composer(token, False)


def make_queryset_from_list(qlist):
    if not qlist:
        return Q()
    current = qlist[0]
    for qobj in qlist[1:]:
        current &= qobj
    return current


def make_queryset_from_or_list(qlist):
    if not qlist:
        return Q()
    current = qlist[0]
    for qobj in qlist[1:]:
        current |= qobj
    return current


def datasearch(params, composer=_dummycomposer):
    """Torna un objecte Q segons un string de cerca.

    ``params`` és l'string amb sintaxis de cerca.
    ``composer`` és una funció que torna un objecte Q. Els seus arguments són:
      * ``key``: una clau simple. S'hauria d'utilizar com
        ``Q(camp__contains=key).``
      * ``exact``: un booleà que indica si el valor ha de ser exacte
    """
    parser = shlex.shlex(params, posix=True)
    parser.commenters = ''
    parser.quotes = ''
    parser.escapedquotes = '"\''
    parser.whitespace_split = True
    current = []
    ors = []
    for token in parser:
        if token == '|':
            ors.append(make_queryset_from_list(current))
            current = []
            continue
        current.append(parse_token(token, composer))
    ors.append(make_queryset_from_list(current))
    return make_queryset_from_or_list(ors)
