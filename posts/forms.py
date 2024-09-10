from django import forms
from .models import Post, DonationRequest ,Comment ,DonationRequestImage, DonationRequestFile
class RegularPostForm(forms.ModelForm):
    author_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Your name (optional for non-registered users)'}))

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'author_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class DonationRequestForm(forms.ModelForm):
    estimated_cost = forms.DecimalField(max_digits=10, decimal_places=2)
    prosthetic_type = forms.CharField(max_length=100)
    measurements = forms.CharField(widget=forms.Textarea)
    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class CommentForm(forms.ModelForm):
    author_name = forms.CharField(max_length=100, required=False, label='Your Name')

    class Meta:
        model = Comment
        fields = ['content', 'author_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author_name'].widget.attrs['placeholder'] = 'Enter your name (optional)'    

class DonationRequestImageForm(forms.ModelForm):
    class Meta:
        model = DonationRequestImage
        fields = ['image']

class DonationRequestFileForm(forms.ModelForm):
    class Meta:
        model = DonationRequestFile
        fields = ['file']

DonationRequestImageFormSet = forms.inlineformset_factory(DonationRequest, DonationRequestImage, form=DonationRequestImageForm, extra=3)
DonationRequestFileFormSet = forms.inlineformset_factory(DonationRequest, DonationRequestFile, form=DonationRequestFileForm, extra=2)