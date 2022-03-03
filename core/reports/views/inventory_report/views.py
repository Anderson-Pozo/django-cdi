import json
from datetime import datetime
from traceback import print_tb

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from core.inventory.models import Bodega, Material
from xhtml2pdf import pisa

from core.school.models import Company
from core.security.mixins import ModuleMixin
from core.reports.forms import ReportForm, Student, Cursos, Period, Inventory, Bodega
from core.reports.utils import link_callback_report


class InventoryReportView(ModuleMixin, FormView):
    template_name = 'inventory_report/report.html'
    form_class = ReportForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_search_data(self):
        bodega = self.request.POST.get('bodega', None)
        print(bodega)
        search = []
        if bodega:
            search = Inventory.objects.filter(material__bodega_id=bodega)
            bodega = Bodega.objects.get(id=bodega)
        else:
            search= Inventory.objects.all()
        
        return search, bodega

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        data = {}
        
        if action == 'search_report':
                data = []
                inventory, _ = self.get_search_data()
                for i in inventory:
                    data.append(i.toJSON())
        elif action == 'generate_pdf':
                inventory, bodega = self.get_search_data()
                context = {
                    'data': inventory,
                    'bodega': bodega,
                    'company': Company.objects.first(),
                    'date_joined': datetime.now().date(),
                    'title': 'Reporte de Sctok del Inventario'
                    
                }
                template = get_template('inventory_report/pdf.html')
                html_template = template.render(context).encode(encoding="UTF-8")
                response = HttpResponse(content_type='application/pdf')
                pisa_status = pisa.CreatePDF(
                    html_template,
                    dest=response,
                    link_callback=link_callback_report
                )
                return response
        else:
                data['error'] = 'No ha ingresado una opción'
        
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Sctok del Inventario'
        return context
