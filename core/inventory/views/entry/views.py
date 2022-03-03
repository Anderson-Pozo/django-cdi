import json

from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.inventory.forms import Entry, EntryForm, Material, EntryMaterial, Inventory
from core.security.mixins import PermissionMixin


class EntryListView(PermissionMixin, ListView):
    model = Entry
    template_name = 'entry/list.html'
    permission_required = ['view_entry', 'view_entrymaterial']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('create_entry')
        context['title'] = 'Listado de entradas'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'search_entries':
                data = []
                for ent in EntryMaterial.objects.filter(entry_id=request.POST['id']):
                    data.append(ent.toJSON())
            else:
                data['error'] = 'No ha selecionado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')


class EntryCreateView(PermissionMixin, CreateView):
    model = Entry
    template_name = 'entry/create.html'
    form_class = EntryForm
    success_url = reverse_lazy('entry_list')
    permission_required = ['add_entry', 'add_entrymaterial']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Nuevo registro de entrada'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'add':
                with transaction.atomic():
                    entry_mat = []
                    items = json.loads(request.POST['items'])
                    entry = Entry(date_entry=items['date_entry'], employee=request.user)
                    entry.save()

                    for m in items['materials']:
                        mat = Material.objects.get(pk=m['id'])
                        cantidad = int(m['cantidad'])
                        entry_mat.append(
                            EntryMaterial(entry=entry, material=mat, amount=cantidad)
                        )
                        if Inventory.objects.filter(material_id=mat.id):
                            invent = Inventory.objects.get(material_id=mat.id)
                            invent.stock += cantidad
                            invent.save()
                        else:
                            Inventory(material=mat, stock=int(m['cantidad'])).save()
                    EntryMaterial.objects.bulk_create(entry_mat)
            elif action == 'search_material':
                data = []
                materials = json.loads(request.POST['materials'])
                for m in Material.objects.filter(
                    name__icontains=request.POST['term']
                ).order_by('name').exclude(id__in=materials)[0:10]:
                    data.append(m.toJSON())
            else:
                data['error'] = 'No se seleccionó una acción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')


class EntryDeleteView(PermissionMixin, DeleteView):
    model = Entry
    template_name = 'entry/delete.html'
    success_url = reverse_lazy('entry_list')
    permission_required = 'delete_entry'

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
