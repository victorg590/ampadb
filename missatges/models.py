from django.db import models
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.functional import cached_property
from datetime import timedelta

class GrupDeMissatgeria(models.Model):
    class Meta:
        verbose_name_plural = 'grups de missatgeria'
    nom = models.CharField(max_length=100)
    usuaris = models.ManyToManyField(User)
    motius = models.TextField(blank=True, help_text='Motius per enviar '
        'missatges a aquest grup. Apareixeràn a "Nou missatge". Un per línia.')

    @cached_property
    def motius_list(self):
        # Separar 'motius'. Si hi ha línies en blanc, les elimina.
        return list(filter(None, self.motius.splitlines()))

    def __str__(self):
        return self.nom

class EstatMissatge(models.Model):
    class Meta:
        verbose_name = 'estat del missatge'
        verbose_name_plural = 'estat dels missatges'
        unique_together = ('destinatari', 'missatge')
    destinatari = models.ForeignKey(User, on_delete=models.CASCADE)
    missatge = models.ForeignKey('Missatge', on_delete=models.CASCADE)
    vist = models.BooleanField(blank=True, default=False)

class Missatge(models.Model):
    class Meta:
        unique_together = ('conversacio', 'ordre')
        ordering = ['-ordre']
    conversacio = models.ForeignKey('Conversacio', on_delete=models.CASCADE,
        blank=False, null=False, verbose_name='conversació')
    per = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False,
        null=True, related_name='ha_enviat')
    destinataris = models.ManyToManyField(User, through='EstatMissatge')
    ordre = models.PositiveSmallIntegerField(editable=False)
    contingut = models.TextField(blank=True,
        help_text='Suporta <a href="/markdown">Markdown</a>')
    enviat = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    editat = models.DateTimeField(auto_now=True, blank=False, null=False)
    estat = models.CharField(max_length=8, blank=True, choices=[
        ('CLOSED', 'Tancat'),
        ('REOPENED', 'Reobert')
    ])

    def ha_sigut_editat(self):
        """Indica si un missatge ha sigut editat"""
        return abs(self.editat - self.enviat) > timedelta(seconds=10)
        # Permet un marge de +/- 10 segons
    ha_sigut_editat.boolean = True
    ha_sigut_editat.short_description = 'Ha sigut editat?'

    def calcular_destinataris(self, vist=False):
        if self.estat:
            # Les notificacions d'estat no tenen destinataris
            return
        if not self.per in self.destinataris.all():
            EstatMissatge.objects.create(destinatari=self.per, missatge=self,
                vist=True)
        for u in (u for u in self.conversacio.a.usuaris.all()
            if u not in self.destinataris.all()):
            EstatMissatge.objects.create(destinatari=u, missatge=self,
                vist=vist)
        self.save()

    def notificar(self, request):
        context = {
            'per': self.per,
            'conversacio': self.conversacio,
            'conversacio_url': request.build_absolute_uri(
                self.conversacio.get_absolute_url()),
            'missatge': self.contingut
        }
        template_path = 'missatges/emails/notificacio.{fmt}'
        txt_loader = loader.get_template(template_path.format(fmt='txt'))
        missatge_txt = txt_loader.render(context)
        html_loader = loader.get_template(template_path.format(fmt='html'))
        missatge_html = html_loader.render(context)
        bcc = [d.email for d in self.destinataris.filter(
            ~Q(email=''),
            email__isnull=False,
        )]  # Filtra els destinataris amb correu
        if not bcc:
            return  # Si no hi ha destinataris, acaba
        msg = EmailMultiAlternatives(
            subject='Nou missatge de {per} a {conversacio}'.format(per=self.per,
                conversacio=self.conversacio),
            body=missatge_txt,
            bcc=bcc
        )
        msg.attach_alternative(missatge_html, 'text/html')
        msg.send()


    def clean(self):
        super().clean()
        if self.contingut and self.estat:
            raise ValidationError("Només un de `contingut` i `estat` es pot "
                "definir")
        elif not (self.contingut or self.estat):
            raise ValidationError("O `contingut` o `estat` s'ha de definir")

    def __str__(self):
        if len(self.contingut) > 80:
            return self.contingut[:77] + '...'
        else:
            return self.contingut

class Conversacio(models.Model):
    class Meta:
        verbose_name = 'conversació'
        verbose_name_plural = 'conversacions'
        ordering = ['creada', 'tancada']

    de = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False,
        null=True)
    a = models.ForeignKey(GrupDeMissatgeria, on_delete=models.SET_NULL,
        blank=False, null=True)
    assumpte = models.CharField(max_length=80)
    tancada = models.BooleanField(blank=True, default=False)
    creada = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        rstr = self.assumpte
        if self.tancada:
            rstr += ' [TANCAT]'
        return rstr

    def get_absolute_url(self):
        return reverse('missatges:show', args=[self.pk])

    def can_access(self, usuari):
        """
        Comprova si una persona està a la conversació i, per tant, si pot
        accedir
        """
        return (usuari == self.de) or (self.a.usuaris.filter(
            username=usuari.username).exists())

    def marcar_com_a_llegits(self, usuari):
        """Marca tots el missatges com a llegits per a l'usuari"""
        for msg in Missatge.objects.filter(conversacio=self):
            EstatMissatge.objects.update_or_create(destinatari=usuari,
                missatge=msg, defaults={'vist': True})

    def tots_llegits(self, usuari):
        """Torna si s'han llegit tots els missatges de la conversació"""
        return not EstatMissatge.objects.filter(destinatari=usuari,
            missatge__in=Missatge.objects.filter(conversacio=self),
            vist=False).exists()
