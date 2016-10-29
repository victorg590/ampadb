from ampadb.support import Forms
from django import forms

_md_text = 'Suporta <a href="/markdown">Markdown</a>'


class ComposeForm(Forms.Form):
    a = forms.CharField(disabled=True, required=False)
    assumpte = forms.CharField(max_length=80)
    missatge = forms.CharField(widget=forms.Textarea, help_text=_md_text)


class ReplyForm(Forms.Form):
    missatge = forms.CharField(widget=forms.Textarea, help_text=_md_text)
