# Generated by Django 4.1.7 on 2023-03-03 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0002_rename_meniitem_menuitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(auto_now_add=True, db_index=True),
        ),
    ]
