from django.shortcuts import render, redirect
from ampadb.support import is_admin
from django.contrib.auth.decorators import login_required
from usermanager.models import Profile


@login_required
def index(request):
    if is_admin(request.user):
        return redirect('contactboard:adminlist')
    else:
        p = Profile.objects.get(user=request.user)
        return redirect('contactboard:list', p.alumne.classe.id_interna)


def markdown_help(request):
    return render(request, 'support/markdown_help.html')
