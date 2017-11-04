from django import template
from django.utils.html import mark_safe
from ..parse_md import parse_md

register = template.Library()


@register.filter
def md(value, arg=''):  # pylint: disable=invalid-name
    if not arg or arg == 'div':
        kwargs = {'wrap': 'div', 'html_class': 'markdown'}
    elif arg == 'blockquote':
        kwargs = {'wrap': 'blockquote', 'html_class': None}
    else:
        kwargs = {'wrap': arg}
    return mark_safe(parse_md(value, **kwargs))


class MarkdownNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        text = self.nodelist.render(context)
        return mark_safe(parse_md(text))


@register.tag(name="markdown")
def do_markdown(parser, _):
    nodelist = parser.parse('endmarkdown')
    parser.delete_first_token()
    return MarkdownNode(nodelist)
