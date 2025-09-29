
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kb_live', '0009_alter_categoryoverallresult_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryoverallresult',
            name='snatch_place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce Snatch'),
        ),
        migrations.AddField(
            model_name='categoryoverallresult',
            name='tgu_place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce TGU'),
        ),
        migrations.AddField(
            model_name='categoryoverallresult',
            name='squat_place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce Squat'),
        ),
        migrations.AddField(
            model_name='categoryoverallresult',
            name='see_saw_press_place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce See-Saw'),
        ),
        migrations.AddField(
            model_name='categoryoverallresult',
            name='pistol_place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce Pistol'),
        ),
        migrations.AddField(
            model_name='categoryoverallresult',
            name='pull_up_place',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Miejsce Pull-Up'),
        ),
    ]
