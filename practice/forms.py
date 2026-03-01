from django import forms

from .models import PracticeLog


class PracticeLogForm(forms.ModelForm):
    class Meta:
        model = PracticeLog
        fields = ['video', 'practiced_on', 'minutes', 'notes']
        widgets = {
            'practiced_on': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

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
