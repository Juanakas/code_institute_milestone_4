from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import PracticeLog


class PracticeLogForm(forms.ModelForm):
    class Meta:
        model = PracticeLog
        fields = ['video', 'practiced_on', 'minutes', 'notes']
        widgets = {
            'video': forms.Select(attrs={'class': 'form-select'}),
            'practiced_on': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 600, 'placeholder': 'e.g. 30'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'What did you practice?'}),
        }

    def clean_practiced_on(self):
        practiced_on = self.cleaned_data['practiced_on']
        if practiced_on > timezone.localdate():
            raise ValidationError('Practice date cannot be in the future.')
        return practiced_on

    def clean_minutes(self):
        minutes = self.cleaned_data['minutes']
        if minutes < 5:
            raise forms.ValidationError('Practice time must be at least 5 minutes.')
        if minutes > 600:
            raise forms.ValidationError('Practice time must be 600 minutes or less.')
        return minutes

    def clean_notes(self):
        notes = self.cleaned_data['notes'].strip()
        if len(notes) < 10:
            raise forms.ValidationError('Notes must be at least 10 characters long.')
        return notes
