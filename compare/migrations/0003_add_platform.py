from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("compare", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="etteremetelinfo",
            name="platform",
            field=models.CharField(default="egyeb", max_length=20, choices=[('wolt', 'Wolt'), ('foodora', 'Foodora'), ('bolt', 'Bolt Food'), ('egyeb', 'Egyéb')]),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='etteremetelinfo',
            unique_together={('etel', 'etterem', 'platform')},
        ),
        migrations.AddIndex(
            model_name='etteremetelinfo',
            index=models.Index(fields=['platform'], name='compare_ett_platform_idx'),
        ),
    ]
