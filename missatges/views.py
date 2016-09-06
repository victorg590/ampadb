from django.shortcuts import render
from .models import GrupDeMissatgeria, Conversacio
from django.contrib.auth.decorators import login_required

@login_required
def list_view(request):
    grups = GrupDeMissatgeria.objects.filter(usuaris=request.user)
    missatges_enviats = Conversacio.objects.filter(de=request.user)
    missatges_rebuts = Conversacio.objects.filter(a=grups)
    context = {
        'grups': grups,
        'missatges_enviats': missatges_enviats,
        'missatges_rebuts': missatges_rebuts
    }
    return render(request, 'missatges/list.html', context)
