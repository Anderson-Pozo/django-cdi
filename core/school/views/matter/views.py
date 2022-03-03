import json

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.school.forms import MatterForm, Matter
from core.security.mixins import  PermissionMixin
#from deep_translator import GoogleTranslator


class MatterListView(PermissionMixin, ListView):
    model = Matter
    template_name = 'matter/list.html'
    permission_required = 'view_matter'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('matter_create')
        context['title'] = 'Listado de Ámbitos'
        return context


class MatterCreateView(PermissionMixin, CreateView):
    model = Matter
    template_name = 'matter/create.html'
    form_class = MatterForm
    success_url = reverse_lazy('matter_list')
    permission_required = 'add_matter'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            name = self.request.POST['name'].strip()
            level = self.request.POST['level']
            if len(level):
                if type == 'name':
                    if Matter.objects.filter(name__icontains=name, level=level):
                        data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                data = self.get_form().save()
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un ámbito'
        context['action'] = 'add'
        return context


class MatterUpdateView(PermissionMixin, UpdateView):
    model = Matter
    template_name = 'matter/create.html'
    form_class = MatterForm
    success_url = reverse_lazy('matter_list')
    permission_required = 'change_matter'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            name = self.request.POST['name'].strip()
            level = self.request.POST['level']
            id = self.get_object().id
            if len(level):
                if type == 'name':
                    if Matter.objects.filter(name__icontains=name, level=level).exclude(id):
                        data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                data = self.get_form().save()
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Ámbito'
        context['action'] = 'edit'
        return context


class MatterDeleteView(PermissionMixin, DeleteView):
    model = Matter
    template_name = 'matter/delete.html'
    success_url = reverse_lazy('matter_list')
    permission_required = 'delete_matter'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            a='Imposible realizar esta acción, ya que este ámbito se encuentra operativo'
           # data['error'] = GoogleTranslator(source='en', target='es').translate(text=str(e)) 
            data['error'] = a
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
