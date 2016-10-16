from django import template
from django.utils.html import format_html, mark_safe
from django.urls import reverse

register = template.Library()


@register.simple_tag
def urllink(text, href, *args, safe=False, classes="", **kwargs):
    """Construeix enllaços amb cerca d'URL

    Exemple::
        <a href"{% url 'a:b' x %}>Text</a>
    És::
        {% urllink 'Text' 'a:b' x}
    Per utilitzar HTML al text, passi ``safe=True``.
    """
    if safe:
        text = mark_safe(text)
    url = reverse(href, args=args, kwargs=kwargs)
    return format_html('<a class="{}" href="{}">{}</a>',
                       classes, url, text)
