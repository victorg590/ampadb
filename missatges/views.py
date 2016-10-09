from django.shortcuts import render, redirect, get_object_or_404
from .models import GrupDeMissatgeria, Conversacio, Missatge
from .forms import ComposeForm, ReplyForm
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
            missatge.notificar()
            return redirect('missatges:list')
    else:
        form = ComposeForm(initial={'a': destinatari})
    context = {
        'form': form
    }
    return render(request, 'missatges/compose.html', context)

@login_required
def show(request, cid):
    conversacio = get_object_or_404(Conversacio, pk=cid)
    if conversacio.can_access(request.user):
        # Marca com a llegit
        conversacio.marcar_com_a_llegits(request.user)
    else:
        return redirect('missatges:list')
    context = {
        'conversacio': conversacio,
        'missatges': Missatge.objects.filter(conversacio=conversacio)
    }
    return render(request, 'missatges/show.html', context)

@login_required
def reply(request, cid):
    conversacio = get_object_or_404(Conversacio, pk=cid)
    if not conversacio.can_access(request.user):
        return redirect('missatges:list')
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            msg = Missatge()
            msg.conversacio = conversacio
            msg.per = request.user
            msg.contingut = form.cleaned_data['missatge']
            msg.save()
            msg.calcular_destinataris()
            msg.notificar()
            return redirect('missatges:show', conversacio.pk)
    else:
        form = ReplyForm()
    context = {
        'form': form
    }
    return render(request, 'missatges/reply.html', context)

@login_required
def close(request, cid):
    conversacio = get_object_or_404(Conversacio, pk=cid)
    if not conversacio.can_access(request.user):
        return redirect('missatges:list')
    if conversacio.tancat:
        msg = Missatge()
        msg.conversacio = conversacio
        msg.per = request.user
        msg.estat = 'REOPENED'
        msg.save()
        conversacio.tancat = False
        conversacio.save()
        return redirect('missatges:show', conversacio.pk)
    else:
        msg = Missatge()
        msg.conversacio = conversacio
        msg.per = request.user
        msg.estat = 'CLOSED'
        msg.save()
        conversacio.tancat = True
        conversacio.save()
        return redirect('missatges:show', conversacio.pk)
