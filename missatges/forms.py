from django import forms

class ComposeForm(forms.Form):
    a = forms.CharField(disabled=True, required=False)
    assumpte = forms.CharField(max_length=80)
    missatge = forms.CharField(widget=forms.Textarea)
