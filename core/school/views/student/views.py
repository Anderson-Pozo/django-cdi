import json

from django.contrib.auth.models import Group
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, DetailView

#print data test
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views import View
from django.http import HttpResponseRedirect
from core.school.models import LegalRepresentative, StudentMedicalRecord


from config import settings
from core.school.forms import StudentForm, User, Student, Parish, StudentMedicalRecord, LegalRepresentative, Family, \
    StudentMedicalRecordForm, LegalRepresentativeForm, FamilyForm, FamilyGroup
from core.security.mixins import ModuleMixin, PermissionMixin
#from deep_translator import GoogleTranslator


class StudentListView(PermissionMixin, TemplateView):
    template_name = 'student/list.html'
    permission_required = 'view_student'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search':
                data = []
                for i in Student.objects.filter():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('student_create')
        context['title'] = 'Listado de Estudiantes'
        return context


class StudentCreateView(PermissionMixin, CreateView):
    model = Student
    template_name = 'student/profile.html'
    form_class = StudentForm
    success_url = reverse_lazy('student_list')
    permission_required = 'add_student'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'dni':
                if User.objects.filter(dni=obj):
                    data['valid'] = False
            elif type == 'mobile':
                if Student.objects.filter(mobile=obj):
                    data['valid'] = False
            elif type == 'email':
                if User.objects.filter(email=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                with transaction.atomic():
                    user = User()
                    user.first_name = request.POST['first_name']
                    user.last_name = request.POST['last_name']
                    user.dni = request.POST['dni']
                    user.username = user.dni
                    if 'image' in request.FILES:
                        user.image = request.FILES['image']
                    user.create_or_update_password(user.dni)
                    user.email = request.POST['email']
                    user.save()
                    student = Student()
                    student.user_id = user.id
                    student.gender = request.POST['gender']
                    student.mobile = request.POST['mobile']
                    student.phone = request.POST['phone']
                    student.address = request.POST['address']
                    student.birthdate = request.POST['birthdate']
                    student.parish_id = int(request.POST['parish']) if request.POST['parish'] else None
                    student.age = int(request.POST['age']) if request.POST['age'] else None
                    student.birth_country_id = int(request.POST['birth_country']) if request.POST[
                        'birth_country'] else None
                    student.birth_province_id = int(request.POST['birth_province']) if request.POST[
                        'birth_province'] else None
                    student.birth_city = request.POST['birth_city']
                    student.nationality = request.POST['nationality']
                    student.ethnicity = request.POST['ethnicity']
                    student.religion = request.POST['religion']
                    student.emergency_number = request.POST['emergency_number']
                    student.save()
                    group = Group.objects.get(pk=settings.GROUPS.get('student'))
                    user.groups.add(group)

                    med_record_form = StudentMedicalRecordForm(request.POST.copy(), request.FILES)
                    med_record_form.data['student'] = student.id
                    med_record_form.save()

                    leg_repr_form = LegalRepresentativeForm(request.POST.copy(), request.FILES)
                    leg_repr_form.data['student'] = student.id
                    leg_repr_form.save()

                    familyjson = json.loads(request.POST['family'])
                    for fam in familyjson:
                        fam_form = FamilyForm(fam)
                        family = fam_form.save()

                        fam_group = FamilyGroup()
                        fam_group.family = family
                        fam_group.student = student
                        fam_group.save()
            elif action == 'search_parish':
                data = []
                term = request.POST['term']
                for i in Parish.objects.filter(name__icontains=term)[0:10]:
                    item = {'id': i.id, 'text': i.__str__(), 'data': i.toJSON()}
                    data.append(item)
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
        context['title'] = 'Nuevo registro de un Estudiante'
        context['action'] = 'add'
        context['frmRecord'] = StudentMedicalRecordForm()
        context['frmRepr'] = LegalRepresentativeForm()
        context['frmFamily'] = FamilyForm()
        context['instance'] = None
        context['tab_add'] = 'active'
        return context


class StudentDeleteView(PermissionMixin, DeleteView):
    model = Student
    template_name = 'student/delete.html'
    success_url = reverse_lazy('student_list')
    permission_required = 'delete_student'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            with transaction.atomic():
                instance = self.get_object()
                user = instance.user
                instance.delete()
                user.delete()
        except Exception as e:
            a='Imposible realizar esta acción, ya que este estudiante ya ha sido matriculado'
            #data['error'] = GoogleTranslator(source='en', target='es').translate(text=str(e)) 
            data['error'] = a

        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context


class StudentDetailView(DetailView):
    model = Student
    template_name = 'student/detail.html'

    def get_medical_record(self):
        student = self.get_object()
        return StudentMedicalRecord.objects.filter(student=student)[0:1]

    def get_legal_representative(self):
        student = self.get_object()
        return LegalRepresentative.objects.filter(student=student)[0:1]

    def get_family(self):
        student = self.get_object()
        return Family.objects.filter(familygroup__student=student)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['create_url'] = reverse_lazy('student_create')
        context['title'] = 'Información del estudiante'
        context['med_record'] = self.get_medical_record()
        context['repr'] = self.get_legal_representative()
        context['family'] = self.get_family()
        return context


class GenericUpdateStudent(UpdateView):
    model = Student
    form_class = StudentForm
    title = ''

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user.student

    def get_family(self):
        data = []
        student = self.get_object()
        try:
            for fam in Family.objects.filter(familygroup__student=student):
                data.append(fam.toJSON())
        except Exception as e:
            print(e)
        return json.dumps(data)

    def get_instance_record(self):
        student = self.get_object()
        result = StudentMedicalRecord.objects.filter(student=student)[0:1]
        if result:
            return result[0]
        return None

    def get_instance_representative(self):
        student = self.get_object()
        result = LegalRepresentative.objects.filter(student=student)[0:1]
        if result:
            return result[0]
        return None

    def get_form_record(self):
        instance = self.get_instance_record()
        return StudentMedicalRecordForm(instance=instance)

    def get_form_representative(self):
        instance = self.get_instance_representative()
        return LegalRepresentativeForm(instance=instance)

    def get_form(self, form_class=None):
        instance = self.object
        form = StudentForm(instance=instance, initial={
            'first_name': instance.user.first_name,
            'last_name': instance.user.last_name,
            'dni': instance.user.dni,
            'email': instance.user.email,
            'image': instance.user.image,
        })
        if instance.parish:
            form.fields['parish'].queryset = Parish.objects.filter(id=instance.parish.id)
        return form

    def remove_docs(self):
        instance_record = self.get_instance_record()
        instance_repr = self.get_instance_representative()

        if 'vcard-clear' in self.request.POST:
            instance_record.remove_vaccine_card()
        elif 'croquis-clear' in self.request.POST:
            instance_repr.remove_croquis()
        elif 'comprob-clear' in self.request.POST:
            instance_repr.remove_payment_bs()
        elif 'image-rpr-clear' in self.request.POST:
            instance_repr.remove_image()

    def validate_data(self):
        data = {'valid': True}
        try:
            instance = self.object
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'dni':
                if User.objects.filter(dni=obj).exclude(id=instance.user.id):
                    data['valid'] = False
            elif type == 'mobile':
                if Student.objects.filter(mobile=obj).exclude(id=instance.id):
                    data['valid'] = False
            elif type == 'email':
                if User.objects.filter(email=obj).exclude(id=instance.user.id):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                with transaction.atomic():
                    instance = self.object
                    user = instance.user
                    user.first_name = request.POST['first_name']
                    user.last_name = request.POST['last_name']
                    user.dni = request.POST['dni']
                    user.username = user.dni
                    if 'image-clear' in request.POST:
                        user.remove_image()
                    if 'image' in request.FILES:
                        user.image = request.FILES['image']
                    user.email = request.POST['email']
                    user.save()

                    student = instance
                    student.user_id = user.id
                    student.gender = request.POST['gender']
                    student.mobile = request.POST['mobile']
                    student.phone = request.POST['phone']
                    student.address = request.POST['address']
                    student.birthdate = request.POST['birthdate']
                    student.parish_id = int(request.POST['parish']) if request.POST['parish'] else None
                    student.age = int(request.POST['age']) if request.POST['age'] else None
                    student.birth_country_id = int(request.POST['birth_country']) if request.POST[
                        'birth_country'] else None
                    student.birth_province_id = int(request.POST['birth_province']) if request.POST[
                        'birth_province'] else None
                    student.birth_city = request.POST['birth_city']
                    student.nationality = request.POST['nationality']
                    student.ethnicity = request.POST['ethnicity']
                    student.religion = request.POST['religion']
                    student.emergency_number = request.POST['emergency_number']
                    student.save()

                    instance_record = self.get_instance_record()
                    med_record_form = StudentMedicalRecordForm(request.POST.copy(), request.FILES,
                                                               instance=instance_record)
                    med_record_form.data['student'] = instance.id
                    med_record_form.save()

                    instance_repr = self.get_instance_representative()
                    leg_repr_form = LegalRepresentativeForm(request.POST.copy(), request.FILES, instance=instance_repr)
                    leg_repr_form.data['student'] = instance.id
                    leg_repr_form.save()

                    # Remove docs from med_record and representative
                    self.remove_docs()
                    Family.objects.filter(familygroup__student=instance).delete()

                    familyjson = json.loads(request.POST['family'])

                    for fam in familyjson:
                        fam_form = FamilyForm(fam)
                        family = fam_form.save()

                        fam_group = FamilyGroup()
                        fam_group.family = family
                        fam_group.student = instance
                        fam_group.save()
            elif action == 'search_parish':
                data = []
                term = request.POST['term']
                for i in Parish.objects.filter(name__icontains=term)[0:10]:
                    item = {'id': i.id, 'text': i.__str__(), 'data': i.toJSON()}
                    data.append(item)
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
        context['title'] = self.title
        context['action'] = 'edit'
        context['frmRecord'] = self.get_form_record()
        context['frmRepr'] = self.get_form_representative()
        context['frmFamily'] = FamilyForm()
        context['family'] = self.get_family()
        context['instance'] = self.object
        context['instance_rpr'] = self.get_instance_representative()
        context['instance_record'] = self.get_instance_record()
        return context


class StudentUpdateProfileView(ModuleMixin, GenericUpdateStudent):
    title = 'Edición del perfil'
    template_name = 'student/profile.html'
    success_url = reverse_lazy('dashboard')

#imprimir hoja PDF de datos 
class print_stud_data(View):
    def get(self, request,*args, **kwargs):
        try:
            template = get_template('student/print_stud_dat.html')
            context= {
                'data': Student.objects.get(pk=self.kwargs['pk']),
                'repre': LegalRepresentative.objects.get(student_id=self.kwargs['pk']),
                'ficha': StudentMedicalRecord.objects.get(student_id=self.kwargs['pk'])
                }
            html = template.render(context)
            response = HttpResponse(content_type='aplication.pdf')
            #para descargar directamente
            #response['Content-Disposition']  = 'attachment; filename="report.pdf"'
            pisaStatus = pisa.CreatePDF(
                html, dest=response)
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('dashboard'))


class StudentUpdateView(PermissionMixin, GenericUpdateStudent):
    title = 'Edición de un estudiante'
    template_name = 'student/profile.html'
    success_url = reverse_lazy('student_list')
    permission_required = 'change_student'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.model.objects.get(pk=pk)
