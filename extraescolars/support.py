from django.utils import timezone
from contactboard.models import Curs


def status_inscripcio(extraescolar, alumne):
    reqs = []
    des_de = extraescolar.inscripcio_des_de
    if des_de:
        ok = timezone.now() > des_de  # pylint: disable=invalid-name
        reqs.append({'ok': ok, 'motiu': 'inici', 'data': des_de})
    fins_a = extraescolar.inscripcio_fins_a
    if fins_a:
        ok = fins_a > timezone.now()  # pylint: disable=invalid-name
        reqs.append({'ok': ok, 'motiu': 'final', 'data': fins_a})
    n_cursos = extraescolar.cursos.count()
    if n_cursos == 0:
        reqs.append({
            'ok': False,
            'motiu': 'cursos',
            'cursos': '[No està disponible per a cap curs]'
        })
    elif n_cursos != Curs.objects.count():
        ok = (  # pylint: disable=invalid-name
            not alumne or extraescolar.cursos.filter(
                id_interna=alumne.classe.curs.id_interna).exists())
        if n_cursos == 1:
            reqs.append({
                'ok': ok,
                'motiu': 'cursos',
                'cursos': str(extraescolar.cursos.all()[0])
            })
        else:
            c_str = ''
            n = 0  # pylint: disable=invalid-name
            for curs in extraescolar.cursos.all():
                n += 1  # pylint: disable=invalid-name
                if n == n_cursos:
                    c_str += 'o ' + str(curs)
                elif n == n_cursos - 1:
                    c_str += str(curs) + ' '
                else:
                    c_str += str(curs) + ', '
            reqs.append({'ok': ok, 'motiu': 'cursos', 'cursos': c_str})
    ok = all([r['ok'] for r in reqs])  # pylint: disable=invalid-name
    return ok, reqs
