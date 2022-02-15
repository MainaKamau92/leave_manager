from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from leaves_manager.apps.organization.forms import OrganizationForm
from leaves_manager.apps.organization.models import Organization


@login_required
def new_organization(request):
    if request.user.organization is not None:
        return redirect('dashboard')
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            user = request.user
            org = Organization.objects.create(**form.cleaned_data)
            org.initial_set_up_complete = True
            org.save()
            user.organization = org
            user.is_org_owner = True
            user.save()
            return redirect('dashboard')
        else:
            for error in form.errors:
                messages.add_message(request, messages.ERROR, form.errors.get(error))
    else:
        form = OrganizationForm()
    return render(request, 'organization/create_org.html', {'form': form})
