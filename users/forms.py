from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, MemberApplication ,  MemberProfile


class CustomUserCreationForm(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    proof_image = forms.ImageField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'date_of_birth')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'password-input'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'password-input'})

class MemberApplicationForm(forms.ModelForm):
    class Meta:
        model = MemberApplication
        fields = ['proof_image']

class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['photo', 'bio']

        from django import forms
from django.contrib.auth.models import User
from .models import MemberProfile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['photo', 'bio']