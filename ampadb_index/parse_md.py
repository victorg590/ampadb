import markdown
import bleach
import lxml.html
from lxml.html import builder as E
import html

TAGS = [
    'p', 'img', 'em', 'strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol',
    'ul', 'li', 'br', 'hr', 'a', 'img', 'blockquote', 'b', 'i', 'u', 's',
    'pre', 'code', 'table', 'thead', 'tr', 'th', 'tbody', 'td'
]

ATTRS = {
    'ol': ['start'], 'a': ['href', 'title', 'rel'],
    'img': ['src', 'title', 'alt'], 'th': ['align'], 'td': ['align']
}

STYLES = []


def clean(raw_html):
    return bleach.clean(raw_html, tags=TAGS, attributes=ATTRS,
                        styles=STYLES)

def parse_md(md, wrap='div', html_class='markdown'):
    raw_html = markdown.markdown(
        md, output_format='html5',
        enable_attributes=False, lazy_ol=False, encoding='utf-8',
        extensions=['markdown.extensions.extra'])
    clean_html = clean(raw_html)
    # Embolica el codi amb l'etiqueta que calgui
    if wrap == 'div':
        if html_class:
            tree = E.DIV(E.CLASS(html_class))
        else:
            tree = E.DIV()
    elif wrap == 'blockquote':
        if html_class:
            tree = E.BLOCKQUOTE(E.CLASS(html_class))
        else:
            tree = E.BLOCKQUOTE()
    elif wrap == 'raw':
        return clean_html
    else:
        raise ValueError('`wrap` ha de ser "div" o "blockquote", no '
                         '{}'.format(wrap))
    bin_html = clean_html.encode('utf-8', 'xmlcharrefreplace')
    try:
        for e in lxml.html.fragments_fromstring(
                bin_html, parser=lxml.html.HTMLParser(encoding='utf-8')):
            tree.append(e)
    except TypeError:
        # S'ha de "desescapar" perque E.P també escapa l'HTML
        tree.append(E.P(html.unescape(clean_html)))
    for table in tree.iter('table'):
         table.classes |= {'table'}  # Afegir la classe "table"
    return lxml.html.tostring(tree, encoding='utf-8', method='html',
                              pretty_print=True).decode('utf-8')
