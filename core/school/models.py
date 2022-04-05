import base64
from email.policy import default
import os
from datetime import datetime
from pickle import TRUE

from PIL import Image
from django.db import models
from django.forms import model_to_dict

from config import settings
from core.school.choices import months, course_level, horary, gender_person, blood_types, civil_state
from core.security.audit_mixin.mixin import AuditMixin
from core.user.models import User

from django.db import IntegrityError, connections, transaction



class Company(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Compañia', max_length=50, unique=True)
    ruc = models.CharField(verbose_name='Ruc', max_length=13, unique=True)
    mobile = models.CharField(verbose_name='Teléfono', max_length=10, unique=True)
    email = models.CharField(verbose_name='Correo Electrónico', max_length=50, unique=True)
    address = models.CharField(verbose_name='Dirección', max_length=255)
    image = models.ImageField(verbose_name='Logo', upload_to='company/%Y/%m/%d', null=True, blank=True)
    mission = models.CharField(verbose_name='Misión', max_length=1000)
    vision = models.CharField(verbose_name='Visión', max_length=1000)
    about_us = models.CharField(verbose_name='Quienes Somos', max_length=1000)
    desc = models.CharField(verbose_name='Descripción', max_length=1000)
    coordinates = models.CharField(verbose_name='Coordenadas', max_length=50)

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return '{}{}'.format(settings.MEDIA_URL, self.image)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def remove_image(self):
        try:
            if self.image:
                os.remove(self.image.path)
        except:
            pass
        finally:
            self.image = None

    def get_latitude(self):
        return self.coordinates.split(',')[0].replace(',', '.')

    def get_longitude(self):
        return self.coordinates.split(',')[1].replace(',', '.')

    def toJSON(self):
        item = model_to_dict(self, exclude=['iva'])
        item['image'] = self.get_image()
        return item

    def get_base64_encoded_image(self):
        try:
            image = base64.b64encode(open(self.image.path, 'rb').read()).decode('utf-8')
            type_image = Image.open(self.image.path).format.lower()
            return "data:image/{};base64,{}".format(type_image, image)
        except:
            pass
        return None

    class Meta:
        verbose_name = 'Compañia'
        verbose_name_plural = 'Compañias'
        default_permissions = ()
        permissions = (
            ('view_company', 'Can view Compañia'),
        )
        db_table = 'empresa'
        ordering = ['-id']


class Country(AuditMixin, models.Model):
    code = models.CharField(max_length=4, verbose_name='Código', unique=True)
    name = models.CharField(max_length=50, verbose_name='Nombre', unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Paises'
        ordering = ['-id']


class Province(AuditMixin, models.Model):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='País')
    name = models.CharField(max_length=50, verbose_name='Nombre', unique=True)
    code = models.CharField(max_length=4, verbose_name='Código', unique=True)

    def __str__(self):
        return 'País: {} / Provincia: {}'.format(self.country.name, self.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['country'] = self.country.toJSON()
        return item

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
        ordering = ['-id']


class Canton(AuditMixin, models.Model):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, verbose_name='Provincia')
    name = models.CharField(max_length=50, verbose_name='Nombre')

    def __str__(self):
        return '{} / Cantón: {}'.format(self.province.__str__(), self.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['province'] = self.province.toJSON()
        return item

    class Meta:
        verbose_name = 'Cantón'
        verbose_name_plural = 'Cantones'
        ordering = ['-id']


class Parish(AuditMixin, models.Model):
    canton = models.ForeignKey(Canton, on_delete=models.PROTECT, verbose_name='Cantón')
    name = models.CharField(max_length=50, verbose_name='Nombre')

    def __str__(self):
        return '{} / Parroquia: {}'.format(self.canton.__str__(), self.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['canton'] = self.canton.toJSON()
        return item

    class Meta:
        verbose_name = 'Parroquia'
        verbose_name_plural = 'Parroquias'
        ordering = ['-id']


class Teacher(AuditMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    gender = models.CharField(max_length=10, choices=gender_person,  verbose_name='Género')
    mobile = models.CharField(max_length=10, unique=True, verbose_name='Teléfono celular')
    email_institucional = models.EmailField(max_length=50, null=True, blank=True, verbose_name="Correo institucional")
    phone = models.CharField(max_length=10, null=True, blank=True, verbose_name='Teléfono convencional')
    birthdate = models.DateField(default=datetime.now, verbose_name='Fecha de nacimiento')
    parish = models.ForeignKey(Parish, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Lugar residencia')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')
    reference = models.CharField(max_length=80, null=True, blank=True, verbose_name='Lugar de referencia')
    nationality = models.CharField(max_length=50, null=True, blank=True, verbose_name='Nacionalidad')
    age = models.IntegerField(null=True, blank=True, verbose_name='Edad')
    ethnicity = models.CharField(max_length=50, null=True, blank=True, verbose_name='Etnia')
    religion = models.CharField(max_length=50, null=True, blank=True, verbose_name='Religión')
    civil_status = models.CharField(max_length=20, choices=civil_state, null=True, blank=True,
                                    verbose_name='Estado civil')
    blood_group = models.CharField(max_length=5, choices=blood_types, null=True, blank=True,
                                   verbose_name='Grupo sanguíneo')
    disability = models.BooleanField(null=True, blank=True, default=False, verbose_name='Discapacidad')
    disability_percentage = models.IntegerField(null=True, blank=True, default=0,
                                                verbose_name='Porcentaje de discapacidad')
    disability_type = models.CharField(max_length=30, null=True, blank=True, verbose_name='Tipo de discapacidad')
    cat_illnesses = models.BooleanField(null=True, blank=True, default=False,
                                        verbose_name='Enfermedades catastróficas')
    cat_illnesses_desc = models.TextField(null=True, blank=True,
                                          verbose_name='Descripción de enfermedades catastróficas')
    croquis = models.FileField(upload_to='teacher/croquis/%Y/%m/%d', null=True, blank=True,
                               verbose_name='Croquis PDF')
    basic_services_payment = models.FileField(upload_to='teacher/bs-payment/%Y/%m/%d', null=True, blank=True,
                                              verbose_name='Comprobante de servicios básicos')
    ci_doc = models.FileField(upload_to='teacher/ci/%Y/%m/%d', null=True, blank=True,
                              verbose_name='Cédula de identidad')
    commitment_act = models.FileField(upload_to='teacher/acta/%Y/%m/%d', null=True, blank=True,
                                      verbose_name='Acta de compromiso')
    contract = models.FileField(upload_to='teacher/contrato/%Y/%m/%d', null=True, blank=True,
                                verbose_name='Contrato firmado')
    cv_doc = models.FileField(upload_to='teacher/cv-doc/%Y/%m/%d', null=True, blank=True,
                              verbose_name='Hoja de vida')

    def __str__(self):
        return '{} / {}'.format(self.user.get_full_name(), self.user.dni)

    def birthdate_format(self):
        return self.birthdate.strftime('%Y-%m-%d')

    def toJSON(self):
        item = model_to_dict(self)
        item['user'] = self.user.toJSON()
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        item['birthdate'] = self.birthdate.strftime('%Y-%m-%d')
        item['parish'] = self.parish.toJSON() if self.parish else ''
        item['croquis'] = self.get_croquis()
        item['basic_services_payment'] = self.get_comprobante()
        item['ci_doc'] = self.get_ci_doc()
        item['commitment_act'] = self.get_commitment_act()
        item['contract'] = self.get_contract()
        item['cv_doc'] = self.get_cv_doc()
        return item

    def remove_cv_doc(self):
        try:
            if self.cv_doc:
                os.remove(self.cv_doc.path)
        except:
            pass
        finally:
            self.cv_doc = None

    def get_croquis(self):
        if self.croquis:
            return '{}{}'.format(settings.MEDIA_URL, self.croquis)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_comprobante(self):
        if self.basic_services_payment:
            return '{}{}'.format(settings.MEDIA_URL, self.basic_services_payment)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_ci_doc(self):
        if self.ci_doc:
            return '{}{}'.format(settings.MEDIA_URL, self.ci_doc)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_commitment_act(self):
        if self.commitment_act:
            return '{}{}'.format(settings.MEDIA_URL, self.commitment_act)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_contract(self):
        if self.contract:
            return '{}{}'.format(settings.MEDIA_URL, self.contract)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_cv_doc(self):
        if self.cv_doc:
            return '{}{}'.format(settings.MEDIA_URL, self.cv_doc)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
        ordering = ['-id']


class Student(AuditMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    gender = models.CharField(max_length=10, choices=gender_person,  verbose_name='Género')#default=gender_person[0][0],
    mobile = models.CharField(max_length=10, unique=True, verbose_name='Teléfono celular')
    phone = models.CharField(max_length=10, null=True, blank=True, verbose_name='Teléfono convencional')
    emergency_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Teléfono de emergencia')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')
    birthdate = models.DateField(default=datetime.now, verbose_name='Fecha de nacimiento')
    parish = models.ForeignKey(Parish, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Parroquia')
    birth_country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True,
                                      verbose_name='País de nacimiento')
    birth_province = models.ForeignKey(Province, on_delete=models.PROTECT, null=True, blank=True,
                                       verbose_name='Provincia de nacimiento')
    birth_city = models.CharField(max_length=30, null=True, blank=True, verbose_name='Ciudad de nacimiento')
    nationality = models.CharField(max_length=50, null=True, blank=True, verbose_name='Nacionalidad')
    age = models.IntegerField(null=True, blank=True, verbose_name='Edad')
    ethnicity = models.CharField(max_length=50, null=True, blank=True, verbose_name='Etnia')
    religion = models.CharField(max_length=50, null=True, blank=True, verbose_name='Religión')

    def __str__(self):
        return '{} / {}'.format(self.user.get_full_name(), self.user.dni)

    def get_full_name(self):
        return self.user.get_full_name()

    def birthdate_format(self):
        return self.birthdate.strftime('%Y-%m-%d')

    def get_info_search_student(self):
        return '{}/{}/{}'.format(self.get_full_name(), self.user.dni, self.birthdate_format())

    def get_repr(self):
        legal_repr = LegalRepresentative.objects.get(student_id=self.id).ci_rp
        if legal_repr is not None:
            return LegalRepresentative.objects.get(student_id=self.id).__str__()
        else:
            return 'Sin asignar'

    def toJSON(self):
        item = model_to_dict(self)
        item['user'] = self.user.toJSON()
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        item['birthdate'] = self.birthdate.strftime('%Y-%m-%d')
        item['parish'] = self.parish.toJSON() if self.parish else ''
        item['full_name'] = self.user.get_full_name()
        item['value'] = self.get_info_search_student()
        return item

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['-id']


class LegalRepresentative(AuditMixin, models.Model):
    first_name_rp = models.CharField(max_length=50, null=True, blank=True, verbose_name='Nombres')
    last_name_rp = models.CharField(max_length=50, null=True, blank=True, verbose_name='Apellidos')
    relationship_rp = models.CharField(max_length=30, null=True, blank=True, verbose_name='Parentesco')
    ci_rp = models.CharField(max_length=10, null=True, blank=True, verbose_name='Cédula de identidad')
    nationality_rp = models.CharField(max_length=50, null=True, blank=True, verbose_name='Nacionalidad')
    address_rp = models.CharField(max_length=70, null=True, blank=True, verbose_name='Dirección')
    reference_rp = models.CharField(max_length=80, null=True, blank=True, verbose_name='Referencia')
    cell_phone_rp = models.CharField(max_length=20, null=True, blank=True, verbose_name='Celular')
    conventional_phone_rp = models.CharField(max_length=20, null=True, blank=True, verbose_name='Teléfono convencional')
    emergency_number_rp = models.CharField(max_length=20, null=True, blank=True, verbose_name='Teléfono de emergencia')
    email_rp = models.EmailField(max_length=30, null=True, blank=True, verbose_name='Correo electrónico')
    blood_group_rp = models.CharField(max_length=5, choices=blood_types, null=True, blank=True,
                                      verbose_name='Grupo sanguíneo')
    is_working_rp = models.BooleanField(null=True, blank=True, default=False, verbose_name='Trabaja')
    workplace_rp = models.CharField(max_length=30, null=True, blank=True, verbose_name='Lugar de trabajo')
    work_phone_rp = models.CharField(max_length=20, null=True, blank=True, verbose_name='Teléfono del trabajo')
    work_address_rp = models.CharField(max_length=70, null=True, blank=True, verbose_name='Dirección del trabajo')
    work_email_rp = models.EmailField(max_length=30, null=True, blank=True, verbose_name='Correo del trabajo')
    croquis_rp = models.FileField(upload_to='rs/croquis/%Y/%m/%d', null=True, blank=True,
                                  verbose_name='Croquis PDF')
    basic_services_payment_rp = models.FileField(upload_to='rs/bs-payment/%Y/%m/%d', null=True, blank=True,
                                                 verbose_name='Comprobante de servicios básicos')
    image_rp = models.ImageField(upload_to='rs/image/%Y/%m/%d', null=True, blank=True, verbose_name='Fotografía')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Estudiante')

    def __str__(self):
        return '{} {}'.format(self.first_name_rp, self.last_name_rp)

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Representante del estudiante'
        verbose_name_plural = 'Representantes del estudiante'
        ordering = ['id']

    def get_image(self):
        if self.image_rp:
            return '{}{}'.format(settings.MEDIA_URL, self.image_rp)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_croquis(self):
        if self.croquis_rp:
            return '{}{}'.format(settings.MEDIA_URL, self.croquis_rp)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def get_comprobante(self):
        if self.basic_services_payment_rp:
            return '{}{}'.format(settings.MEDIA_URL, self.basic_services_payment_rp)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def remove_croquis(self):
        try:
            if self.croquis_rp:
                os.remove(self.croquis_rp.path)
        except:
            pass
        finally:
            self.croquis_rp = None
            self.save()

    def remove_payment_bs(self):
        try:
            if self.basic_services_payment_rp:
                os.remove(self.basic_services_payment_rp.path)
        except:
            pass
        finally:
            self.basic_services_payment_rp = None
            self.save()

    def remove_image(self):
        try:
            if self.image_rp:
                os.remove(self.image_rp.path)
        except:
            pass
        finally:
            self.image_rp = None
            self.save()


class StudentMedicalRecord(AuditMixin, models.Model):
    weight = models.DecimalField(decimal_places=2, default=0.00, max_digits=5, blank=True, null=True,
                                 verbose_name='Peso')
    size = models.CharField(max_length=20, null=True, blank=True, verbose_name='Talla')
    height = models.DecimalField(decimal_places=2, default=0.00, max_digits=5, blank=True, null=True,
                                 verbose_name='Altura')
    blood_group = models.CharField(max_length=5, choices=blood_types, null=True, blank=True,
                                   verbose_name='Grupo sanguíneo')
    donor = models.BooleanField(null=True, blank=True, default=False, verbose_name='Donante')
    vaccine_card = models.FileField(upload_to='smr/vaccinecard/%Y/%m/%d', null=True, blank=True,
                                    verbose_name='Carnet de vacunas')
    disability = models.BooleanField(null=True, blank=True, default=False, verbose_name='Discapacidad')
    disability_type = models.CharField(max_length=30, null=True, blank=True, verbose_name='Tipo de discapacidad')
    disability_per = models.IntegerField(null=True, blank=True, verbose_name='Porcentaje de discapacidad')
    allergies = models.BooleanField(null=True, blank=True, default=False, verbose_name='Alergias')
    allergies_desc = models.TextField(null=True, blank=True, verbose_name='Descripción de las alergias')
    allergy_treatment = models.CharField(max_length=50, null=True, blank=True,
                                         verbose_name='Tratamiento de las alergias')
    diseases_suffered = models.BooleanField(null=True, blank=True, default=False, verbose_name='Enfermedades padecidas')
    diseases_suffered_desc = models.TextField(null=True, blank=True,
                                              verbose_name='Descripción de enfermedades padecidas')
    pre_diseases = models.BooleanField(null=True, blank=True, default=False,
                                       verbose_name='Enfermedades preexistentes')
    pre_diseases_desc = models.TextField(null=True, blank=True,
                                         verbose_name='Descripción de enfermedades preexistentes')
    cat_illnesses = models.BooleanField(null=True, blank=True, default=False,
                                        verbose_name='Enfermedades catastróficas')
    cat_illnesses_desc = models.TextField(null=True, blank=True,
                                          verbose_name='Descripción de enfermedades catastróficas')
    medication = models.BooleanField(null=True, blank=True, default=False, verbose_name='Medicación')
    medication_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='Tipo de medicación')
    medication_schedule = models.CharField(max_length=50, null=True, blank=True, verbose_name='Horario de medicación')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Estudiante')

    def __str__(self):
        return self.student.__str__()

    def toJSON(self):
        item = model_to_dict(self)
        return item

    def get_vaccine_card(self):
        if self.vaccine_card:
            return '{}{}'.format(settings.MEDIA_URL, self.vaccine_card)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def remove_vaccine_card(self):
        try:
            if self.vaccine_card:
                os.remove(self.vaccine_card.path)
        except:
            pass
        finally:
            self.vaccine_card = None
            self.save()

    class Meta:
        verbose_name = 'Ficha médica'
        verbose_name_plural = 'Fichas médicas'
        ordering = ['id']


class Family(AuditMixin, models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='Nombres')
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='Apellidos')
    ci = models.CharField(max_length=10, null=True, blank=True, verbose_name='Cédula de identidad')
    relationship = models.CharField(max_length=30, null=True, blank=True, verbose_name='Parentesco')
    age = models.IntegerField(null=True, blank=True, verbose_name='Edad')
    civil_status = models.CharField(max_length=20, choices=civil_state, null=True, blank=True,
                                    verbose_name='Estado civil')
    disability = models.BooleanField(null=True, blank=True, default=False, verbose_name='Discapacidad')
    disability_type = models.CharField(max_length=30, null=True, blank=True, verbose_name='Tipo de discapacidad')
    cat_illnesses = models.BooleanField(null=True, blank=True, default=False,
                                        verbose_name='Enfermedades catastróficas')
    cat_illnesses_desc = models.TextField(null=True, blank=True,
                                          verbose_name='Descripción de enfermedades catastróficas')
    academic_training = models.CharField(max_length=50, null=True, blank=True, verbose_name='Formación académica')
    occupation = models.CharField(max_length=30, null=True, blank=True, verbose_name='Ocupación')
    economic_income = models.DecimalField(decimal_places=2, default=0.00, max_digits=9, blank=True, null=True,
                                          verbose_name='Ingresos')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def toJSON(self):
        item = model_to_dict(self)
        item['economic_income'] = format(self.economic_income, '.2f')
        return item

    class Meta:
        verbose_name = 'Familiar'
        verbose_name_plural = 'Familiares'
        ordering = ['id']

    def delete_family(self):
        FamilyGroup.objects.filter(family_id=self.id).delete()
        self.delete()


class FamilyGroup(AuditMixin, models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Estudiante')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Familiar')

    class Meta:
        verbose_name = 'Grupo familiar'
        verbose_name_plural = 'Grupos familiares'
        ordering = ['id']

    def __str__(self):
        return '{} {} {}'.format(self.id, self.family, self.student)


class TypeCVitae(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo de Hoja de Vida'
        verbose_name_plural = 'Tipos de Hoja de Vida'
        ordering = ['id']


class CVitae(AuditMixin, models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, verbose_name='Profesor')
    typecvitae = models.ForeignKey(TypeCVitae, on_delete=models.PROTECT, verbose_name='Tipo')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    details = models.CharField(max_length=5000, null=True, blank=True, verbose_name='Detalles')
    start_date = models.DateField(default=datetime.now, verbose_name='Fecha de inicio')
    end_date = models.DateField(default=datetime.now, verbose_name='Fecha de finalización')
    cv_file = models.FileField(upload_to='teacher/cv/%Y/%m/%d', null=True, blank=True,
                               verbose_name='Archivo')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['teacher'])
        item['typecvitae'] = self.typecvitae.toJSON()
        item['cv_file'] = {"name": self.get_cv_file()}
        item['start_date'] = self.start_date.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        return item

    def get_cv_file(self):
        if self.cv_file:
            return '{}{}'.format(settings.MEDIA_URL, self.cv_file)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    class Meta:
        verbose_name = 'Hoja de Vida'
        verbose_name_plural = 'Hojas de Vida'
        ordering = ['id']


class Job(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Puesto de Trabajo'
        verbose_name_plural = 'Puesto de Trabajos'
        ordering = ['id']

class ConferenceTheme(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tema de Conferencia'
        verbose_name_plural = 'Temas de Conferencias'
        ordering = ['id']


class Shifts(AuditMixin, models.Model):
    name = models.CharField(max_length=50, verbose_name='Nombre', unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['-id']


class Contracts(AuditMixin, models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, verbose_name='Profesor')
    job = models.ForeignKey(Job, on_delete=models.PROTECT, verbose_name='Cargo')
    shifts = models.ForeignKey(Shifts, on_delete=models.PROTECT, verbose_name='Turno', default="1")
    start_date = models.DateField(default=datetime.now, verbose_name='Fecha de inicio', null=TRUE)
    end_date = models.DateField(default=datetime.now, verbose_name='Fecha de finalización', null=TRUE)
    base_salary = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Salario Base')
    state = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return '{} / {}'.format(self.teacher.user.get_full_name(), self.job.name)

    def nro(self):
        return format(self.id, '06d')

    def toJSON(self):
        item = model_to_dict(self)
        item['nro'] = format(self.id, '06d')
        item['base_salary'] = format(self.base_salary, '.2f')
        item['teacher'] = self.teacher.toJSON()
        item['shifts'] = self.shifts.toJSON()
        item['job'] = self.job.toJSON()
        item['start_date'] = self.start_date.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        return item

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['id']


class TypeEvent(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)
    economic_sanction = models.BooleanField(default=False, verbose_name='Sanción económica')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'
        ordering = ['id']


class Events(AuditMixin, models.Model):
    contract = models.ForeignKey(Contracts, on_delete=models.PROTECT, verbose_name='Contrato')
    typeevent = models.ForeignKey(TypeEvent, on_delete=models.PROTECT, verbose_name='Tipo de Evento')
    start_date = models.DateField(default=datetime.now, verbose_name='Fecha de inicio')
    end_date = models.DateField(default=datetime.now, verbose_name='Fecha de finalización')
    start_time = models.TimeField(default=datetime.now, verbose_name='Hora de inicio')
    end_time = models.TimeField(default=datetime.now, verbose_name='Hora de finalización')
    desc = models.CharField(max_length=2000, null=True, blank=True, verbose_name='Detalles')
    valor = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='Valor')
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.typeevent.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-id']


class Assistance(AuditMixin, models.Model):
    date_joined = models.DateField(default=datetime.now)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, related_name='fk_teacher')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='fk_user')
    year = models.IntegerField()
    month = models.IntegerField(choices=months, default=0)
    day = models.IntegerField()
    desc = models.CharField(max_length=500, null=True, blank=True)
    state = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.get_month_display()

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['month'] = {'id': self.month, 'name': self.get_month_display()}
        item['user'] = self.user.toJSON()
        return item

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        default_permissions = ()
        permissions = (
            ('view_assistance', 'Can view Asistencias'),
            ('add_assistance', 'Can add Asistencias'),
            ('delete_assistance', 'Can delete Asistencias'),
        )
        ordering = ['id']


class Cursos(AuditMixin, models.Model):
    name = models.CharField(max_length=23, null=False, blank=False, verbose_name='Nombre')
    descrip = models.CharField(max_length=70, null=False, blank=False, verbose_name='Descripción')
    max_coupon = models.IntegerField( null=True, blank=True, verbose_name='Cupo máximo de estudiantes')
    min_coupon = models.IntegerField( null=True, blank=True, verbose_name='Cupo mínimo de estudiantes')

    # state = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['id']


class Matter(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50)
    level = models.ForeignKey(Cursos, on_delete=models.PROTECT, max_length=30, verbose_name='Curso')
    state = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.name

    # def toJSON(self):
    #    item = model_to_dict(self)
    #    item['level'] = {'id': self.level, 'name': self.level.name()}
    #    return item

    def toJSON(self):
        item = model_to_dict(self)
        item['level'] = self.level.toJSON()
        item['value'] = self.name
        return item

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['id']


class Conferences(AuditMixin, models.Model):
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de conferencia')
    name = models.CharField(max_length=50, verbose_name='Nombre')
    contract = models.ForeignKey(Contracts, on_delete=models.PROTECT, verbose_name='Profesor')
    conferencetheme = models.ForeignKey(ConferenceTheme, on_delete=models.PROTECT, verbose_name='Tema de Conferencia')
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['contract'] = self.contract.toJSON()
        item['conferencetheme'] = self.conferencetheme.toJSON()
        return item

    class Meta:
        verbose_name = 'Tema de Conferencia'
        verbose_name_plural = 'Temas de Conferencias'
        ordering = ['id']


class Period(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)
    initial_date = models.DateField(verbose_name='Fecha de inicio', blank=True, null=True)
    end_date = models.DateField(verbose_name='Fecha final', blank=True, null=True)
    state = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['initial_date'] = self.initial_date.strftime('%Y-%m-%d') if self.initial_date else ''
        item['end_date'] = self.end_date.strftime('%Y-%m-%d') if self.end_date else ''
        return item

    def is_time_over(self):
        today = datetime.now().date()
        if self.end_date < today:
            return True
        return False

    class Meta:
        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'
        ordering = ['id']


class PeriodDetail(AuditMixin, models.Model):
    period = models.ForeignKey(Period, on_delete=models.PROTECT)
    contract = models.ForeignKey(Contracts, on_delete=models.PROTECT)
    matter = models.ForeignKey(Matter, on_delete=models.PROTECT)

    def __str__(self):
        return self.period.name

    def toJSON(self):
        item = model_to_dict(self)
        item['period'] = self.period.toJSON()
        item['contract'] = self.contract.toJSON()
        item['matter'] = self.matter.toJSON()
        return item

    class Meta:
        verbose_name = 'Periodo Detalle'
        verbose_name_plural = 'Periodos Detalles'
        ordering = ['id']


class Tutorials(AuditMixin, models.Model):
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    contract = models.ForeignKey(Contracts, on_delete=models.PROTECT, verbose_name='Profesor')
    horary = models.CharField(max_length=100, choices=horary, verbose_name='Horario')
    desc = models.CharField(max_length=500, verbose_name='Descripción')

    def __str__(self):
        return self.contract.teacher.user.get_full_name()

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tutoría'
        verbose_name_plural = 'Tutorías'
        ordering = ['id']


class Matriculation(AuditMixin, models.Model):
    date_joined = models.DateField(default=datetime.now)
    period = models.ForeignKey(Period, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    # level = models.CharField(choices=course_level, max_length=30)
    level = models.ForeignKey(Cursos, on_delete=models.PROTECT, max_length=30, verbose_name='Nivel')

    def __str__(self):
        return 'Alumno: {} / Número de cédula: {} /  Periodo: {}'.format(self.student.user.get_full_name(),
                                                                         self.student.user.dni,
                                                                         self.period.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['student'] = self.student.toJSON()
        item['period'] = self.period.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['level'] = self.level.toJSON()
        return item

    class Meta:
        verbose_name = 'Matriculación'
        verbose_name_plural = 'Matriculaciones'
        ordering = ['id']


class MatriculationDetail(AuditMixin, models.Model):
    matriculation = models.ForeignKey(Matriculation, on_delete=models.PROTECT)
    perioddetail = models.ForeignKey(PeriodDetail, on_delete=models.PROTECT)

    def __str__(self):
        return self.matriculation.student.user.get_full_name()

    def toJSON(self):
        item = model_to_dict(self)
        item['perioddetail'] = self.perioddetail.toJSON()
        return item

    class Meta:
        verbose_name = 'Matriculación ámbito'
        verbose_name_plural = 'Matriculaciones ámbitos'
        ordering = ['id']


class PsychologicalOrientation(AuditMixin, models.Model):
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    matriculation = models.ForeignKey(Matriculation, on_delete=models.PROTECT, verbose_name='Alumno')
    desc = models.CharField(max_length=5000, verbose_name='Detalles')

    def __str__(self):
        return self.desc

    def toJSON(self):
        item = model_to_dict(self)
        item['matriculation'] = self.matriculation.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        return item

    class Meta:
        verbose_name = 'Orientación Psicológica'
        verbose_name_plural = 'Orientaciones Psicológica'
        ordering = ['id']


class Breakfast(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)
    state = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Desayuno'
        verbose_name_plural = 'Desayunos'
        ordering = ['id']


class SchoolFeeding(AuditMixin, models.Model):
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    breakfast = models.ForeignKey(Breakfast, on_delete=models.PROTECT, verbose_name='Tipo de colación')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, verbose_name='Estudiante')
    cant = models.IntegerField(default=0, verbose_name='Cantidad')
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')

    def __str__(self):
        return self.breakfast.name

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['student'] = self.student.toJSON()
        item['breakfast'] = self.breakfast.toJSON()
        item['desc'] = 'Ninguna' if self.desc is None else self.desc
        return item

    class Meta:
        verbose_name = 'Alimentación escolar'
        verbose_name_plural = 'Alimentación escolares'
        ordering = ['id']


class TypeResource(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo de Recurso'
        verbose_name_plural = 'Tipos de Recursos'
        ordering = ['id']


class Resources(AuditMixin, models.Model):
    typeresource = models.ForeignKey(TypeResource, on_delete=models.PROTECT, verbose_name='Tipo de Recurso')
    perioddetail = models.ForeignKey(PeriodDetail, on_delete=models.PROTECT, verbose_name='Matería')
    start_date = models.DateField(default=datetime.now, verbose_name='Fecha de inicio')
    end_date = models.DateField(default=datetime.now, verbose_name='Fecha de finalización')
    web_address = models.CharField(max_length=200, verbose_name='Enlace')
    desc = models.CharField(max_length=1500, verbose_name='Descripción')

    def __str__(self):
        return self.web_address

    def toJSON(self):
        item = model_to_dict(self)
        item['typeresource'] = self.typeresource.toJSON()
        item['perioddetail'] = self.perioddetail.toJSON()
        item['start_date'] = self.start_date.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        return item

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['id']


class TypeActivity(AuditMixin, models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo de Actividad'
        verbose_name_plural = 'Tipos de Actividades'
        ordering = ['id']


class Activities(AuditMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    typeactivity = models.ForeignKey(TypeActivity, on_delete=models.PROTECT, verbose_name='Tipo de Actividad')
    perioddetail = models.ForeignKey(PeriodDetail, on_delete=models.PROTECT, verbose_name='Materia')
    start_date = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    web_address = models.CharField(max_length=200, verbose_name='Enlace')
    rubric = models.ImageField(upload_to='activities/%Y/%m/%d', null=True, blank=True, verbose_name='Rubrica')
    punctuation = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    desc = models.CharField(max_length=1500, verbose_name='Descripción')
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.web_address

    def remove_rubric(self):
        try:
            if self.rubric:
                os.remove(self.rubric.path)
        except:
            pass
        finally:
            self.image = None

    def get_rubric(self):
        if self.rubric:
            return '{}{}'.format(settings.MEDIA_URL, self.rubric)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def toJSON(self):
        item = model_to_dict(self)
        item['typeactivity'] = self.typeactivity.toJSON()
        item['perioddetail'] = self.perioddetail.toJSON()
        item['start_date'] = self.start_date.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        item['rubric'] = self.get_rubric()
        item['punctuation'] = format(self.punctuation, '.2f')
        return item

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['id']


class Qualifications(AuditMixin, models.Model):
    activities = models.ForeignKey(Activities, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    archive = models.ImageField(upload_to='qualifications/%Y/%m/%d', null=True, blank=True)
    date_joined = models.DateField(default=datetime.now)
    note = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    comment = models.CharField(max_length=200, null=True, blank=True)
    state = models.BooleanField(default=False)

    def __str__(self):
        return self.comment

    def get_archive(self):
        if self.archive:
            return '{}{}'.format(settings.MEDIA_URL, self.archive)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%d-%m-%Y')
        item['archive'] = self.get_archive()
        item['activities'] = self.activities.toJSON()
        item['comment'] = '' if self.comment is None else self.comment
        item['student'] = self.student.toJSON()
        item['note'] = format(self.note, '.2f')
        return item

    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        ordering = ['id']


class NoteDetails(AuditMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    typeactivity = models.ForeignKey(TypeActivity, on_delete=models.PROTECT, verbose_name='Tipo de Actividad')
    perioddetail = models.ForeignKey(PeriodDetail, on_delete=models.PROTECT, verbose_name='Materia')
    start_date = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    desc = models.CharField(max_length=1500, verbose_name='Descripción')
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['typeactivity'] = self.typeactivity.toJSON()
        item['perioddetail'] = self.perioddetail.toJSON()
        item['start_date'] = self.start_date.strftime('%Y-%m-%d')
        item['end_date'] = self.end_date.strftime('%Y-%m-%d')
        return item

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        ordering = ['id']


class Scores(AuditMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    score = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['score'] = format(self.score, '.2f')
        return item

    class Meta:
        verbose_name = 'RB Puntaje'
        verbose_name_plural = 'RB Puntajes'
        ordering = ['id']


class Punctuations(AuditMixin, models.Model):
    notedetails = models.ForeignKey(NoteDetails, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    date_joined = models.DateField(default=datetime.now)
    score = models.ForeignKey(Scores, on_delete=models.PROTECT)
    note = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    comment = models.CharField(max_length=200, null=True, blank=True, default='')
    state = models.BooleanField(default=False)
    evidence_doc = models.FileField(upload_to='punctuations/%Y/%m/%d', null=True, blank=True,
                                    verbose_name='Documento de evidencia')

    def __str__(self):
        return self.comment

    def exists_evidence_doc(self):
        return True if self.evidence_doc else False

    def get_evidence_doc(self):
        if self.evidence_doc:
            return '{}{}'.format(settings.MEDIA_URL, self.evidence_doc)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%d-%m-%Y')
        item['notedetails'] = self.notedetails.toJSON()
        item['comment'] = '' if self.comment is None else self.comment
        item['student'] = self.student.toJSON()
        item['score'] = self.score.toJSON()
        item['note'] = format(self.note, '.2f')
        item['evidence_doc'] = self.get_evidence_doc()
        item['exists_doc'] = self.exists_evidence_doc()
        return item

    class Meta:
        verbose_name = 'Puntaje'
        verbose_name_plural = 'Puntajes'
        ordering = ['id']





class ProtectedError(IntegrityError):
    def __init__(self, msg, protected_objects):
        self.protected_objects = protected_objects
        super().__init__(msg, protected_objects)


    def CASCADE(collector, field, sub_objs, using):
        collector.collect(sub_objs, source=field.remote_field.model,
                        source_attr=field.name, nullable=field.null)
        if field.null and not connections[using].features.can_defer_constraint_checks:
            collector.add_field_update(field, None, sub_objs)



    def PROTECT(collector, field, sub_objs, using):
        raise ProtectedError(
            "xxxxxxxxxxxx '%s' because they are "
            "referenced through a protected foreign key: '%s.%s'" % (
                field.remote_field.model.__name__, sub_objs[0].__class__.__name__, field.name
            ),
            sub_objs
        )



    def SET(value):
        if callable(value):
            def set_on_delete(collector, field, sub_objs, using):
                collector.add_field_update(field, value(), sub_objs)
        else:
            def set_on_delete(collector, field, sub_objs, using):
                collector.add_field_update(field, value, sub_objs)
        set_on_delete.deconstruct = lambda: ('django.db.models.SET', (value,), {})
        return set_on_delete



    def SET_NULL(collector, field, sub_objs, using):
        collector.add_field_update(field, None, sub_objs)



    def SET_DEFAULT(collector, field, sub_objs, using):
        collector.add_field_update(field, field.get_default(), sub_objs)



    def DO_NOTHING(collector, field, sub_objs, using):
        pass



    def get_candidate_relations_to_delete(opts):
        # The candidate relations are the ones that come from N-1 and 1-1 relations.
        # N-N  (i.e., many-to-many) relations aren't candidates for deletion.
        return (
            f for f in opts.get_fields(include_hidden=True)
            if f.auto_created and not f.concrete and (f.one_to_one or f.one_to_many)
        )