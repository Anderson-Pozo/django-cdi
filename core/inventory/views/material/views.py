import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from core.security.mixins import PermissionMixin
from core.inventory.forms import Material, MaterialForm


class MaterialListView(PermissionMixin, ListView):
    model = Material
    template_name = 'material/list.html'
    permission_required = 'view_material'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('create_material')
        context['title'] = 'Listado de materiales didácticos'
        return context


class MaterialCreateView(PermissionMixin, CreateView):
    model = Material
    template_name = 'material/create.html'
    permission_required = 'add_material'
    success_url = reverse_lazy('material_list')
    form_class = MaterialForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Nuevo registro de material'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                data = self.get_form().save()
            else:
                data['error'] = 'No se ha seleccionado una acción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')


class MaterialUpdateView(PermissionMixin, UpdateView):
    model = Material
    template_name = 'material/create.html'
    form_class = MaterialForm
    success_url = reverse_lazy('material_list')
    permission_required = 'change_material'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de material'
        context['action'] = 'edit'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                data = self.get_form().save()
            else:
                data['error'] = 'No ha seleccionado una acción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')


class MaterialDeleteView(PermissionMixin, DeleteView):
    model = Material
    template_name = 'material/delete.html'
    success_url = reverse_lazy('material_list')
    permission_required = 'delete_material'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            a='Imposible realizar esta acción, ya que este material tiene transacciones'
            #data['error'] = str(e)
            data['error'] = a
        return HttpResponse(json.dumps(data), content_type='application/json')
