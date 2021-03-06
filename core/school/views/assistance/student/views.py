import json
from datetime import datetime

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from core.school.forms import AssistanceForm, Assistance
from core.security.mixins import PermissionMixin


class AssistanceStudentListView(PermissionMixin, FormView):
    form_class = AssistanceForm
    template_name = 'assistance/student/list.html'
    permission_required = 'view_assistance'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search':
                data = []
                start_date = request.POST.get('start_date', datetime.now().date().strftime('%Y-%m-%d'))
                end_date = request.POST.get('end_date', datetime.now().date().strftime('%Y-%m-%d'))
                if len(start_date) and len(end_date):
                    for a in Assistance.objects.filter(
                            date_joined__range=[start_date, end_date],
                            is_teacher=False,
                            user=request.user):
                        data.append(a.toJSON())
            else:
                data['error'] = 'No ha seleccionado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de asistencias'
        return context
