from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ampadb.support import is_admin
from usermanager.models import Profile


@login_required
def index(request):
    if is_admin(request.user):
        return redirect('contactboard:adminlist')
    profile = Profile.objects.get(user=request.user)
    return redirect('contactboard:list', profile.alumne.classe.id_interna)


def markdown_help(request):
    return render(request, 'support/markdown_help.html')


def search_syntax(request):
    return render(request, 'support/search_syntax.html')
