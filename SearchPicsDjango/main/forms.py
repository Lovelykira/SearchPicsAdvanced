from django import forms
from django.contrib.auth import authenticate

from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label=u'Имя пользователя', widget=forms.TextInput(attrs={'class': 'login-username'}))
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(attrs={'class': 'login-pass'}))

    def clean(self):
        #cleaned_data = super(LoginForm, self).clean()
        if not self.errors:
            user = authenticate(username=self.cleaned_data.get('username'), password=self.cleaned_data.get('password'))
            if user is None:
                raise forms.ValidationError(u'Пользователя с таким именем и паролем не существует.')
            self.user = user
        return self.cleaned_data

    def get_authenticated_user(self):
        return self.user


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(attrs={'class': 'registr-pass1'}))
    password2 = forms.CharField(label=u'Еще раз пароль', widget=forms.PasswordInput(attrs={'class': 'registr-pass2'}))

    class Meta:
        model = User
        fields = ('username',)
        widgets = {'username': forms.TextInput(attrs={'class': 'reqistr-username'}),
                   }

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return self.cleaned_data