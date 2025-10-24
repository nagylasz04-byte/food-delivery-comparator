from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Felhasznalo


class FelhasznaloCreationForm(UserCreationForm):
    class Meta:
        model = Felhasznalo
        fields = ("username", "nev", "email", "kedvenc_etterem")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # kedvenc_etterem should be optional in the registration form
        if 'kedvenc_etterem' in self.fields:
            self.fields['kedvenc_etterem'].required = False


class FelhasznaloUpdateForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput, help_text="Hagyja üresen, ha nem akarja megváltoztatni a jelszót.")

    class Meta:
        model = Felhasznalo
        fields = ("username", "nev", "email", "kedvenc_etterem", "is_active", "is_staff")

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user
