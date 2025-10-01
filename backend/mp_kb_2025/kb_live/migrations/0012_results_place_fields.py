
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kb_live", "0011_categoryoverallresult_index_rename"),
    ]

    operations = [
        migrations.AddField(
            model_name='snatchresult',
            name='place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce'),
        ),
        migrations.AddField(
            model_name='tguresult',
            name='place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce'),
        ),
        migrations.AddField(
            model_name='squatresult',
            name='place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce'),
        ),
        migrations.AddField(
            model_name='seesawpressresult',
            name='place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce'),
        ),
        migrations.AddField(
            model_name='pistolresult',
            name='place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce'),
        ),
        migrations.AddField(
            model_name='pullupresult',
            name='place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce'),
        ),
    ]
