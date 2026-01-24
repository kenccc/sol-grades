from django import forms

class LoginForm(forms.Form):
    sol_username = forms.CharField(label="SkolaOnline Username")
    sol_password = forms.CharField(
        label="SkolaOnline Password",
        widget=forms.PasswordInput
    )
