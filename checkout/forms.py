from datetime import date

from django import forms

from .models import CheckoutFeedback


class CheckoutPreviewForm(forms.Form):
    full_name = forms.CharField(max_length=100, label='Full name')
    email = forms.EmailField(label='Email address')
    address_line_1 = forms.CharField(max_length=150, label='Address line 1')
    city = forms.CharField(max_length=80, label='City')
    postal_code = forms.CharField(max_length=20, label='Postal code')
    country = forms.CharField(max_length=80, label='Country')

    cardholder_name = forms.CharField(max_length=100, label='Name on card')
    card_number = forms.CharField(max_length=24, label='Card number')
    expiry_month = forms.IntegerField(min_value=1, max_value=12, label='Expiry month')
    expiry_year = forms.IntegerField(min_value=2000, max_value=2100, label='Expiry year')
    cvc = forms.CharField(max_length=4, min_length=3, label='CVC')

    accept_terms = forms.BooleanField(label='I understand this is a demo checkout for academic purposes.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_fields = [
            'full_name', 'email', 'address_line_1', 'city', 'postal_code', 'country',
            'cardholder_name', 'card_number', 'expiry_month', 'expiry_year', 'cvc',
        ]
        for field_name in text_fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        self.fields['accept_terms'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['card_number'].widget.attrs.update({'placeholder': '4242 4242 4242 4242'})
        self.fields['cvc'].widget.attrs.update({'placeholder': '123'})

    def clean_card_number(self):
        raw_number = self.cleaned_data['card_number']
        digits = ''.join(ch for ch in raw_number if ch.isdigit())
        if len(digits) < 13 or len(digits) > 19:
            raise forms.ValidationError('Enter a valid card number.')
        return digits

    def clean_cvc(self):
        raw_cvc = self.cleaned_data['cvc'].strip()
        if not raw_cvc.isdigit() or len(raw_cvc) not in (3, 4):
            raise forms.ValidationError('Enter a valid CVC.')
        return raw_cvc

    def clean(self):
        cleaned_data = super().clean()
        month = cleaned_data.get('expiry_month')
        year = cleaned_data.get('expiry_year')

        if month is None or year is None:
            return cleaned_data

        today = date.today()
        if year < today.year or (year == today.year and month < today.month):
            self.add_error('expiry_year', 'Card expiry date cannot be in the past.')

        return cleaned_data


class CheckoutFeedbackForm(forms.ModelForm):
    class Meta:
        model = CheckoutFeedback
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share what worked well or what can be improved.',
            }),
        }
