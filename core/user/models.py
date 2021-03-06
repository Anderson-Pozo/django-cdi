# -*- codign: utf-8 -*-
from datetime import datetime
import os
import uuid

from crum import get_current_request
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms.models import model_to_dict

from config import settings
from core.security.audit_mixin.mixin import AuditMixin


class User(AuditMixin, AbstractUser):
    dni = models.CharField(max_length=13, unique=True, verbose_name='Cédula o RUC')
    image = models.ImageField(upload_to='users/%Y/%m/%d', verbose_name='Imagen', null=True, blank=True)
    is_change_password = models.BooleanField(default=False)
    token = models.UUIDField(primary_key=False, editable=False, null=True, blank=True, default=uuid.uuid4, unique=True)
    failed_attempts = models.IntegerField(null=True, blank=True, default=0)
    last_login_attempt = models.DateField(blank=True, null=True)
    is_new = models.BooleanField(default=True)

    def toJSON(self):
        item = model_to_dict(self, exclude=['last_login', 'token', 'password', 'user_permissions'])
        item['image'] = self.get_image()
        item['full_name'] = self.get_full_name()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['groups'] = self.get_groups()
        item['last_login'] = None if self.last_login is None else self.last_login.strftime('%Y-%m-%d')
        item['last_login_attempt'] = None
        return item

    def generate_token(self):
        return uuid.uuid4()

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

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image.path)
        except:
            pass
        super(User, self).delete()

    def get_groups(self):
        data = []
        for i in self.groups.all():
            data.append({'id': i.id, 'name': i.name})
        return data

    def get_group_id_session(self):
        try:
            request = get_current_request()
            return int(request.session['group'].id)
        except:
            return 0

    def set_group_session(self):
        try:
            request = get_current_request()
            groups = request.user.groups.all()
            if groups:
                if 'group' not in request.session:
                    request.session['group'] = groups[0]
        except:
            pass

    def create_or_update_password(self, password):
        try:
            if self.pk is None:
                self.set_password(password)
            else:
                user = User.objects.get(pk=self.pk)
                if user.password != password:
                    self.set_password(password)
        except:
            pass

    def is_client(self):
        try:
            if hasattr(self, 'client'):
                return True
        except:
            pass
        return False

    def __str__(self):
        return '{} / {}'.format(self.get_full_name(), self.dni)

    def increment_failed_attempts(self):
        today = datetime.now().date()
        if today != self.last_login_attempt:
            self.failed_attempts = 0
            self.save()
        self.failed_attempts += 1
        self.last_login_attempt = today
        self.save()

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.last_login_attempt = datetime.now().date()
        self.save()

    def is_change_password_as_true(self):
        self.is_change_password = True
        self.save()
