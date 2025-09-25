"""Ensure max_counted_disciplines column exists for Category."""

from django.db import migrations, models


def ensure_max_counted_disciplines(apps, schema_editor):
    """Add the missing max_counted_disciplines column if the table lacks it."""

    connection = schema_editor.connection
    Category = apps.get_model("kb_live", "Category")
    table_name = Category._meta.db_table

    existing_tables = connection.introspection.table_names()
    if table_name not in existing_tables:
        return

    with connection.cursor() as cursor:
        columns = {col.name for col in connection.introspection.get_table_description(cursor, table_name)}

    if "max_counted_disciplines" in columns:
        return

    field = models.PositiveSmallIntegerField(
        verbose_name="Liczba punktowanych konkurencji",
        null=True,
        blank=True,
        help_text=(
            "Ile najlepszych wyników (najniższe miejsca) wliczać do sumy. "
            "Pozostaw puste aby liczyć wszystkie."
        ),
    )
    field.set_attributes_from_name("max_counted_disciplines")
    schema_editor.add_field(Category, field)


def noop(apps, schema_editor):
    """No-op reverse migration."""


class Migration(migrations.Migration):
    dependencies = [
        ("kb_live", "0007_alter_player_gender"),
    ]

    operations = [
        migrations.RunPython(ensure_max_counted_disciplines, noop),
    ]
