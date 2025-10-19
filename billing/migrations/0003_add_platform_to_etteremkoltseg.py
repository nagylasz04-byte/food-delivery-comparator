# Generated migration: add platform field and allow etterem nullable on EtteremKoltseg
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_alter_etteremkoltseg_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='etteremkoltseg',
            name='platform',
            field=models.CharField(blank=True, max_length=20, choices=[('wolt', 'Wolt'), ('foodora', 'Foodora'), ('bolt', 'Bolt Food'), ('egyeb', 'Egyéb')]),
        ),
        migrations.AlterField(
            model_name='etteremkoltseg',
            name='etterem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='koltsegek', to='catalog.etterem'),
        ),
    ]
