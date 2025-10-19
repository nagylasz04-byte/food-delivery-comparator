from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_add_platform_to_etteremkoltseg'),
    ]

    operations = [
        migrations.AddField(
            model_name='etteremkoltseg',
            name='etel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='koltsegek', to='catalog.etel', verbose_name='\u00c9tel'),
        ),
    ]
