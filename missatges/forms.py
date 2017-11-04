from ampadb.support import Forms
from django import forms

_MD_TEXT = 'Suporta <a href="/markdown">Markdown</a>'


class ComposeForm(Forms.Form):
    a = forms.CharField(disabled=True, required=False)  # pylint: disable=invalid-name
    assumpte = forms.CharField(max_length=80)
    missatge = forms.CharField(widget=forms.Textarea, help_text=_MD_TEXT)


class ReplyForm(Forms.Form):
    missatge = forms.CharField(widget=forms.Textarea, help_text=_MD_TEXT)
