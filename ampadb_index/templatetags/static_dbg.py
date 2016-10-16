from django import template
from django.templatetags.static import static
from pathlib import PurePath
from ampadb import settings

register = template.Library()


@register.simple_tag
def static_dbg(path, debug=None):
    """Com `static`, però si no DEBUG, torna la versió minimitzada."""
    if debug is None:
        debug = settings.DEBUG
    path = PurePath(path)
    ext = ''.join(path.suffixes)
    if not debug and ext in ('.css', '.js'):
        changed_ext = PurePath(path.parent, path.stem)
        return static(str(changed_ext.with_suffix('.min' + ext)))
    else:
        return static(str(path))
