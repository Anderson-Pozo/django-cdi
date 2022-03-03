
import ckeditor.fields
import core.security.audit_mixin.mixin
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Web',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Centro infantil')),
                ('ruc', models.CharField(max_length=13, unique=True, verbose_name='Ruc')),
                ('mobile', models.CharField(max_length=10, unique=True, verbose_name='Teléfono')),
                ('email', models.CharField(max_length=50, unique=True, verbose_name='Correo Electrónico')),
                ('address', models.CharField(max_length=255, verbose_name='Dirección')),
                ('image', models.ImageField(blank=True, null=True, upload_to='company/%Y/%m/%d', verbose_name='Imagen Menu')),
                ('image_about', models.ImageField(blank=True, default='', null=True, upload_to='company/%Y/%m/%d', verbose_name='Imagen Nosotros')),
                ('mission', models.CharField(max_length=1000, verbose_name='Misión')),
                ('vision', models.CharField(max_length=1000, verbose_name='Visión')),
                ('about_us', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('desc', models.CharField(max_length=1000, verbose_name='Descripción')),
                ('coordinates', models.CharField(max_length=50, verbose_name='Coordenadas')),
                ('servicios_text', models.CharField(default='', max_length=1000, verbose_name='Servicios')),
                ('docentes_text', models.CharField(default='', max_length=1000, verbose_name='Edades')),
                ('infraestructura_text', models.CharField(default='', max_length=1000, verbose_name='Horarios')),
                ('block1', models.CharField(default='', max_length=1000, verbose_name='Criterios de los niños')),
                ('block2', models.CharField(default='', max_length=1000, verbose_name='Grupos de trabajo')),
                ('block3', models.CharField(default='', max_length=1000, verbose_name='Tarifas y pagos')),
            ],
            options={
                'verbose_name': 'Web',
                'verbose_name_plural': 'Webs',
                'db_table': 'web',
                'ordering': ['-id'],
                'permissions': (('view_web', 'Can view Web'),),
                'default_permissions': (),
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
    ]
