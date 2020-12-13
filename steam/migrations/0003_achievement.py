# Generated by Django 3.1.4 on 2020-12-10 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('steam', '0002_app'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(max_length=256)),
                ('achieved', models.BooleanField()),
                ('unlock_time', models.DateTimeField()),
                ('name', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=256)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='steam.app')),
            ],
        ),
    ]