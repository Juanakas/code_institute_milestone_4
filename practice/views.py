from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


class PracticeLogForm(forms.Form):
	practiced_on = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
	minutes = forms.IntegerField(min_value=1)
	video = forms.CharField(required=False)
	notes = forms.CharField(widget=forms.Textarea)


@login_required
def practice_list(request):
	return render(request, 'practice/log_list.html', {'logs': []})


@login_required
def practice_create(request):
	if request.method == 'POST':
		form = PracticeLogForm(request.POST)
		if form.is_valid():
			messages.success(request, 'Practice log saved.')
			return redirect('practice:list')
	else:
		form = PracticeLogForm()

	return render(request, 'practice/log_form.html', {'form': form, 'is_edit': False})


@login_required
def practice_edit(request, log_id):
	if request.method == 'POST':
		form = PracticeLogForm(request.POST)
		if form.is_valid():
			messages.success(request, 'Practice log updated.')
			return redirect('practice:list')
	else:
		form = PracticeLogForm()

	return render(request, 'practice/log_form.html', {'form': form, 'is_edit': True, 'log_id': log_id})
