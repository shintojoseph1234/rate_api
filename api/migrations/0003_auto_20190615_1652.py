# Generated by Django 2.2.2 on 2019-06-15 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190615_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regions',
            name='parent_slug',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name=models.Model),
        ),
    ]