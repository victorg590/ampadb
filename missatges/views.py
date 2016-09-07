from django.shortcuts import render, redirect, get_object_or_404
from .models import GrupDeMissatgeria, Conversacio, Missatge
from .forms import ComposeForm
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

@login_required
def new(request):
    grups = []
    for g in GrupDeMissatgeria.objects.all():
        grups += [(m, g) for m in g.motius_list]
    context = {
        'grups': grups
    }
    return render(request, 'missatges/new.html', context)

@login_required
def compose(request, to):
    destinatari = get_object_or_404(GrupDeMissatgeria, pk=to)
    if request.method == 'POST':
        form = ComposeForm(request.POST, initial={'a': destinatari})
        if form.is_valid():
            cdata = form.cleaned_data
            conversacio = Conversacio()
            conversacio.de = request.user
            conversacio.a = destinatari
            conversacio.assumpte = cdata['assumpte']
            conversacio.save()
            missatge = Missatge(conversacio=conversacio)
            missatge.per = request.user
            missatge.contingut = cdata['missatge']
            missatge.save()
            missatge.calcular_destinataris()
            return redirect('missatges:list')
    else:
        form = ComposeForm(initial={'a': destinatari})
    context = {
        'form': form
    }
    return render(request, 'missatges/compose.html', context)
