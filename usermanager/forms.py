from ampadb.support import Forms
from django import forms
from django.core import validators
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UnregisteredUser
from django.contrib.auth.models import User


def validate_username_unique(value):
    if (User.objects.filter(username=value).exists() or
            UnregisteredUser.objects.filter(username=value).exists()):
        raise ValidationError('Username exists!')


def validate_alumne_unique(value):
    if Profile.objects.filter(alumne=value).exists():
        raise ValidationError('Alumne already has a user associated!')


class UsersForms:
    class NewForm(Forms.Form):
        alumne = forms.CharField(disabled=True, required=False)
        username = forms.CharField(
            label="Nom d'usuari", max_length=30,
            help_text='Fins a 30 caracters (lletres, números i ".@+-")',
            required=True, validators=[
                validators.RegexValidator(r'^[\w.@+-]+$'),
                validate_username_unique
            ])
        codi = forms.CharField(
            label='Codi', max_length=6,
            required=False, validators=[
                validators.RegexValidator(r'^([0-9]{6})?$')
            ],
            help_text=(
                "Un codi numèric de 6 dígits per confirmar que l'usuari "
                "pertany a aquesta persona. Si no s'entra cap, es generarà un "
                "automàticament."))

    class NewAdminForm(Forms.Form):
        username = forms.CharField(
            label="Nom d'usuari", max_length=30,
            help_text='Fins a 30 caracters (lletres, números i ".@+-")',
            required=True, validators=[
                validators.RegexValidator(r'^[\w.@+-]+$'),
                validate_username_unique
            ])
        password = forms.CharField(
            label='Contrasenya', required=True, widget=forms.PasswordInput)
        password_confirm = forms.CharField(
            label='Confirmar contrasenya', widget=forms.PasswordInput,
            required=True)
        email = forms.EmailField(label='Correu electrònic', required=True)

        def clean(self):
            cleaned_data = super().clean()
            password = cleaned_data.get('password')
            passwordConfirm = cleaned_data.get('password_confirm')
            if password:
                validate_password(password)
            if password and password != passwordConfirm:
                self.add_error('password_confirm',
                               forms.ValidationError(
                                    'La confirmació de contrasenya no és'
                                    ' correcta'))


class RegisterForm(Forms.Form):
    username = forms.CharField(
        label="Nom d'usuari", max_length=30,
        help_text="Utilitza el nom d'usuari que et van donar",
        validators=[validators.RegexValidator(r'^[\w.@+-]+$')],
        required=True, error_messages={
            'required': "Introdueix un nom d'usuari",
            'invalid': "Aquest nom d'usuari no és vàlid"
        })
    _codierr = 'Aquest codi no és vàlid'
    codi = forms.CharField(
        label='Codi', max_length=6,
        widget=forms.PasswordInput,
        help_text='Utilitza el codi que et van donar per al teu usuari',
        validators=[validators.RegexValidator(r'^[0-9]{6}$')],
        required=True, error_messages={
            'invalid': _codierr,
            'required': _codierr
        })
    password = forms.CharField(
        label='Contrasenya', widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(
        label='Confirmar contrasenya', widget=forms.PasswordInput,
        required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        codi = cleaned_data.get('codi')
        password = cleaned_data.get('password')
        passwordConfirm = cleaned_data.get('password_confirm')
        if password:
            validate_password(password)
        if password and password != passwordConfirm:
            self.add_error('password_confirm',
                           ValidationError('La confirmació de contrasenya no '
                                           ' és correcta'))
        if username and codi:
            if not UnregisteredUser.objects.filter(
                    username=username, codi=codi).exists():
                raise forms.ValidationError('No hi ha cap usuari amb aquest'
                                            ' nom i codi')


class AdminChangePasswordForm(Forms.Form):
    password = forms.CharField(
        label='Nova contrasenya', widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(
        label='Confirmar contrasenya', widget=forms.PasswordInput,
        required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        passwordConfirm = cleaned_data.get('password_confirm')
        if password:
            validate_password(password)
        if password and password != passwordConfirm:
            self.add_error('password_confirm',
                           forms.ValidationError(
                                'La confirmació de contrasenya no és'
                                ' correcta'))


class ChangeCodeForm(Forms.Form):
    codi = forms.CharField(
        label='Codi', max_length=6,
        validators=[validators.RegexValidator(r'^[0-9]{6}$')],
        help_text=(
            "Un codi numèric de 6 dígits per confirmar que l'usuari "
            "pertany a aquesta persona."))
