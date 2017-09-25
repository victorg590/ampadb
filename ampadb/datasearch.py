import shlex
from django.db.models.query_utils import Q


def _dummycomposer(key, exact): return Q()


def parse_token(token, composer):
    if '|' in token:
        first, *other = token.split('|')
        current = parse_token(first, composer)
        for t in other:
            current |= parse_token(t, composer)
        return current
    elif token[0] == '"':
        return composer(token[1:-1], False)
    elif token[0] == "'":
        return composer(token[1:-1], True)
    else:
        return composer(token, False)


def make_queryset_from_list(qlist):
    if not qlist:
        return Q()
    current = qlist[0]
    for q in qlist[1:]:
        current &= q
    return current


def make_queryset_from_or_list(qlist):
    if not qlist:
        return Q()
    current = qlist[0]
    for q in qlist[1:]:
        current |= q
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
