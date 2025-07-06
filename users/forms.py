from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, MemberApplication, MemberProfile, MemberVerificationImage

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class CustomUserCreationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date of Birth"
    )
    verification_files = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'accept': 'image/*,.pdf,.doc,.docx',
            'class': 'form-control-file'
        }),
        required=True,
        label="Verification Documents",
        help_text="Upload 6+ files: Government ID, medical documents, prosthetic prescriptions, etc."
    )

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

class MemberVerificationImageForm(forms.ModelForm):
    class Meta:
        model = MemberVerificationImage
        fields = ['image', 'image_type', 'description']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'image_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description (optional)'
            })
        }

# Create formset for multiple verification images (6 images as requested)
MemberVerificationImageFormSet = forms.inlineformset_factory(
    MemberApplication, 
    MemberVerificationImage, 
    form=MemberVerificationImageForm, 
    extra=6,  # Allow 6 additional images
    max_num=10,  # Maximum 10 total images
    can_delete=True
)