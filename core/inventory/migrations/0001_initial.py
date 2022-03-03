

import core.security.audit_mixin.mixin
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bodega',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Bodega',
                'verbose_name_plural': 'Bodegas',
                'ordering': ['id'],
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_entry', models.DateField(default=datetime.datetime.now, verbose_name='Fecha de ingreso')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Entrada',
                'verbose_name_plural': 'Entradas',
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EntryMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(blank=True, null=True, verbose_name='Cantidad')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Entrada material',
                'verbose_name_plural': 'Entrada de materiales',
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.IntegerField(blank=True, null=True, verbose_name='Stock')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Inventario',
                'verbose_name_plural': 'Inventarios',
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('image', models.ImageField(blank=True, null=True, upload_to='materials/%Y/%m/%d', verbose_name='Imagen')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Material',
                'verbose_name_plural': 'Materiales',
                'ordering': ['-id'],
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Output',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_output', models.DateField(default=datetime.datetime.now, verbose_name='Fecha de salida')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Salida',
                'verbose_name_plural': 'Salidas',
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OutputMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(blank=True, null=True, verbose_name='Cantidad')),
                ('fecha_created', models.DateTimeField(auto_now_add=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Material')),
                ('output', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Output')),
            ],
            options={
                'verbose_name': 'Salida material',
                'verbose_name_plural': 'Salida de materiales',
            },
            bases=(core.security.audit_mixin.mixin.AuditMixin, models.Model),
        ),
    ]
