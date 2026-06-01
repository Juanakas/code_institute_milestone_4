from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from subscriptions.decorators import subscription_required

from .forms import PracticeLogForm
from .models import PracticeLog


@login_required
@subscription_required
def practice_list(request):
    logs = PracticeLog.objects.filter(user=request.user).select_related('video')
    return render(request, 'practice/log_list.html', {'logs': logs})


@login_required
@subscription_required
def practice_create(request):
    if request.method == 'POST':
        form = PracticeLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            messages.success(request, 'Practice log saved.')
            return redirect('practice:list')
    else:
        form = PracticeLogForm()

    return render(request, 'practice/log_form.html', {'form': form, 'is_edit': False})


@login_required
@subscription_required
def practice_edit(request, log_id):
    log = get_object_or_404(PracticeLog, id=log_id, user=request.user)
    if request.method == 'POST':
        form = PracticeLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, 'Practice log updated.')
            return redirect('practice:list')
    else:
        form = PracticeLogForm(instance=log)

    return render(request, 'practice/log_form.html', {'form': form, 'is_edit': True, 'log': log})


@login_required
@subscription_required
def practice_delete(request, log_id):
    log = get_object_or_404(PracticeLog, id=log_id, user=request.user)
    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Practice log deleted.')
    return redirect('practice:list')
