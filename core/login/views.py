import datetime
import json
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, RedirectView, TemplateView

from config import settings
from core.login.forms import ResetPasswordForm, ChangePasswordForm
from core.security.models import AccessUsers
from core.user.models import User
from core.login.utils import send_mail_thread


class LoginAuthView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login/login.html'

    def get_form(self, form_class=None):
        form = super(LoginAuthView, self).get_form()
        form.fields['username'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'Ingrese su número de cédula',
            'autocomplete': 'off',
            'autofocus': True
        }
        form.fields['password'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            'autocomplete': 'off',
        }
        return form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        login_different = reverse_lazy('login_different')
        if request.user.is_authenticated and login_different != request.path:
            return HttpResponseRedirect(reverse_lazy('login_authenticated'))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if user.is_new:
            messages.info(self.request, 'Antes de ingresar al sistema debe cambiar su contraseña')
            user.is_change_password_as_true()
            return redirect(f'/login/change/password/{user.token}/')
        if user.is_change_password:
            messages.info(
                self.request,
                'Esta cuenta esta temporalmente bloqueada, revise su correo electrónico'
            )
            return super().get(self.request, self.args, self.kwargs)
        login(self.request, form.get_user())
        if self.request.user.is_authenticated:
            self.request.user.set_group_session()
            AccessUsers(user=self.request.user).save()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = self.get_user_attempt()
            if user:
                user.reset_failed_attempts()
            return self.form_valid(form)
        else:
            self.verify_login_attempts()
            return self.form_invalid(form)

    def get_user_attempt(self):
        form = self.get_form()
        users = User.objects.filter(username=form.data['username'])
        if users.exists():
            return users[0]
        return None

    def verify_login_attempts(self):
        user: User = self.get_user_attempt()
        if user:
            if user.failed_attempts < 5:
                if not user.is_change_password:
                    user.increment_failed_attempts()
                else:
                    messages.info(
                        self.request,
                        'Esta cuenta esta temporalmente bloqueada, revise su correo electrónico'
                    )
            if user.failed_attempts == 5:
                self.send_email_reset_password(user)
                user.is_change_password_as_true()
                user.reset_failed_attempts()
                messages.info(
                    self.request,
                    'Se ha detectado 5 intentos de sesión inválidos, '
                    'se ha enviado un correo a esta cuenta para el cambio de contraseña'
                )

    def send_email_reset_password(self, user: User):
        template_name = 'login/email_reset_pwd.html'
        with transaction.atomic():
            url = settings.LOCALHOST if not settings.DEBUG else self.request.META['HTTP_HOST']
            user.is_change_password = True
            user.save()
            activate_account = '{}{}{}{}'.format('http://', url, '/login/change/password/', user.token)

        send_mail_thread('Cambio de contraseña', user.email, template_name, {
            'user': user,
            'link_resetpwd': activate_account,
            'link_home': f'http://{url}',
            'host': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname())
        })


class LoginAuthenticatedView(TemplateView):
    template_name = 'login/login_authenticated.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ResetPasswordView(FormView):
    template_name = 'login/reset_pwd.html'
    form_class = ResetPasswordForm
    success_url = settings.LOGIN_URL

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def send_email_reset_pwd(self, user):
        with transaction.atomic():
            url = settings.LOCALHOST if not settings.DEBUG else self.request.META['HTTP_HOST']
            user.is_change_password = True
            user.save()

            activate_account = '{}{}{}{}'.format('http://', url, '/login/change/password/', user.token)
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Reseteo de contraseña'
            message['From'] = settings.EMAIL_HOST_USER
            message['To'] = user.email

            parameters = {
                'user': user,
                'link_resetpwd': activate_account,
                'link_home': 'http://{}'.format(url)
            }

            html = render_to_string('login/send_email.html', parameters)
            content = MIMEText(html, 'html')
            message.attach(content)
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(
                settings.EMAIL_HOST_USER, user.email, message.as_string()
            )
            server.quit()

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                self.send_email_reset_pwd(form.get_user())
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reseteo de contraseña'
        return context


class ChangePasswordView(FormView):
    template_name = 'login/change_pwd.html'
    form_class = ChangePasswordForm
    success_url = settings.LOGIN_URL

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = kwargs['pk']
        if User.objects.filter(token=token, is_change_password=True).exists():
            return super().get(request, *args, **kwargs)
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                user = User.objects.get(token=kwargs['pk'])
                user.is_change_password = False
                if user.is_new:
                    user.is_new = False
                user.set_password(request.POST['password'])
                user.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cambio de contraseña'
        return context


class LogoutRedirectView(RedirectView):
    pattern_name = 'login'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)
