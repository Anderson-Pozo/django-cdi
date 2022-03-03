import json

from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DeleteView

from core.security.mixins import PermissionMixin

from core.inventory.forms import Output, OutputForm, Inventory, Material, OutputMaterial


class OutputListView(PermissionMixin, ListView):
    model = Output
    template_name = 'output/list.html'
    permission_required = 'view_output'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('create_output')
        context['title'] = 'Listado de salidas'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'search_outputs':
                data = []
                for ent in OutputMaterial.objects.filter(output_id=request.POST['id']):
                    data.append(ent.toJSON())
            else:
                data['error'] = 'No ha selecionado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')


class OutputCreateView(PermissionMixin, CreateView):
    model = Output
    template_name = 'output/create.html'
    form_class = OutputForm
    success_url = reverse_lazy('output_list')
    permission_required = 'add_output'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Nuevo registro de salida'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'add':
                with transaction.atomic():
                    output_mat = []
                    items = json.loads(request.POST['items'])
                    teacher = int(request.POST['teacher'])
                    output = Output(date_output=items['date_output'], teacher_id=teacher)
                    output.save()

                    for m in items['materials']:
                        mat = Material.objects.get(pk=m['material']['id'])
                        cantidad = int(m['cantidad'])
                        output_mat.append(
                            OutputMaterial(output=output, material=mat, amount=cantidad)
                        )
                        if Inventory.objects.filter(material_id=mat.id):
                            invent = Inventory.objects.get(material_id=mat.id)
                            if invent.stock >= cantidad:
                                invent.stock -= cantidad
                                invent.save()
                            else:
                                raise ValueError('Revise que la cantidad no exceda las existencias')
                    OutputMaterial.objects.bulk_create(output_mat)
            elif action == 'search_material':
                data = []
                materials = json.loads(request.POST['materials'])
                print(materials)
                for m in Inventory.objects.filter(
                    material__name__icontains=request.POST['term'],
                    stock__gt=0
                ).exclude(material_id__in=materials)[0:10]:
                    data.append(m.toJSON())
            else:
                data['error'] = 'No se seleccionó una acción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')


class OutputDeleteView(PermissionMixin, DeleteView):
    model = Output
    template_name = 'output/delete.html'
    success_url = reverse_lazy('output_list')
    permission_required = 'delete_output'

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
