from django import forms
from .models import Donation, DonationComment
from decimal import Decimal

class DonationForm(forms.ModelForm):
    AMOUNT_CHOICES = [
        (10, '$10'),
        (25, '$25'),
        (50, '$50'),
        (100, '$100'),
        (250, '$250'),
        (500, '$500'),
        (1000, '$1000'),
    ]
    
    # Predefined amounts
    predefined_amount = forms.ChoiceField(
        choices=[('', 'Select Amount')] + AMOUNT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'setPredefinedAmount(this.value)'
        })
    )
    
    # Custom amount
    amount = forms.DecimalField(
        min_value=Decimal('1.00'),
        max_value=Decimal('50000.00'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter custom amount',
            'step': '0.01',
            'min': '1.00'
        })
    )
    
    donor_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name (optional for anonymous donations)'
        })
    )
    
    donor_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    
    message = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional message of support...'
        })
    )
    
    is_anonymous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Make this donation anonymous'
    )
    
    class Meta:
        model = Donation
        fields = ['amount', 'donor_name', 'donor_email', 'message', 'is_anonymous']
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount < Decimal('1.00'):
            raise forms.ValidationError('Minimum donation amount is $1.00')
        return amount
    
    def clean(self):
        cleaned_data = super().clean()
        is_anonymous = cleaned_data.get('is_anonymous')
        donor_name = cleaned_data.get('donor_name')
        
        # If not anonymous, require donor name
        if not is_anonymous and not donor_name:
            self.add_error('donor_name', 'Name is required for non-anonymous donations')
        
        return cleaned_data

class QuickDonationForm(forms.Form):
    """Simplified form for quick donations with preset amounts"""
    amount = forms.ChoiceField(
        choices=[
            ('10', '$10'),
            ('25', '$25'),
            ('50', '$50'),
            ('100', '$100'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'quick-amount-radio'})
    )
    
    donor_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email for donation receipt'
        })
    )

class DonationCommentForm(forms.ModelForm):
    content = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your thoughts or message of support...'
        })
    )
    
    is_public = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Make this comment public'
    )
    
    class Meta:
        model = DonationComment
        fields = ['content', 'is_public']