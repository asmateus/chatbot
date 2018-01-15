# Generated by Django 2.0.1 on 2018-01-15 21:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('description', models.TextField(blank=True, max_length=600)),
                ('location', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='origin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='origin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='target', to=settings.AUTH_USER_MODEL),
        ),
    ]
