from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.views.generic import TemplateView
from django.db.models import Count


from core.security.models import Dashboard
from core.security.models import Logs
from core.user.models import User

from core.school.models import Student, Teacher, Period, Cursos
from core.inventory.models import *


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        request.user.set_group_session()
        data = self.get_context_data()
        dashboard = Dashboard.objects.filter()
        if dashboard.exists():
            if dashboard[0].layout == 1:
                return render(request, 'vtcpanel.html', data)
        return render(request, 'hztpanel.html', data)

    @staticmethod
    def get_last_logs():
        try:
            return Logs.objects.all().order_by('-action_time')[0:7]
        except Exception as error:
            print(error)
        return []

    @staticmethod
    def get_last_users():
        try:
            return User.objects.filter(last_login__isnull=False).order_by('-last_login')[0:7]
        except Exception as error:
            print(error)
        return []

    def get_total_students(self):
        try:
            return Student.objects.count()
        except Exception as error:
            print(error)
        return []

    def get_total_teachers(self):
        try:
            return Teacher.objects.count()
        except Exception as error:
            print(error)
        return []

    def get_total_periods(self):
        try:
            return Period.objects.count()
        except Exception as error:
            print(error)
        return []

    def get_total_materiales(self):
        try:
            return EntryMaterial.objects.count()
        except Exception as error:
            print(error)
        return []

    def get_total_inventory(self):
        data = []
        try:
            for inv in Inventory.objects.all():
                data.append({
                    'name': inv.material.name,
                    'y': inv.stock
                })
        except Exception as error:
            print(error)
        return data

    def get_total_levels(self):
        data = []
        try:
            for c in Cursos.objects.all():
                teacher = Teacher.objects.filter(
                    contracts__perioddetail__matriculationdetail__matriculation__level=c
                ).count()
                data.append({
                    'name': c.name,
                    'y': teacher,
                })
        except Exception as error:
            print(error)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Panel de administración'
        context['logs'] = self.get_last_logs()
        context['users'] = self.get_last_users()
        context['stu_count'] = self.get_total_students()
        context['teac_count'] = self.get_total_teachers()
        context['peri_count'] = self.get_total_periods()
        context['materi_count'] = self.get_total_materiales()
        context['get_total_inventory'] = self.get_total_inventory()
        context['get_total_levels'] = self.get_total_levels()

        return context


@requires_csrf_token
def error_404(request, exception):
    return render(request, '404.html', {})


@requires_csrf_token
def error_500(request, exception):
    return render(request, '500.html', {})
