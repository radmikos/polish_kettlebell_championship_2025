
from django.db import migrations, models


FIELD_NAME = "placement_points"
INDEX_NAME = "kb_live_cat_categor_0d5b6a_idx"


def _column_exists(schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        columns = schema_editor.connection.introspection.get_table_description(cursor, table_name)
    return any(col.name == column_name for col in columns)


def _index_exists(schema_editor, table_name, index_name):
    with schema_editor.connection.cursor() as cursor:
        constraints = schema_editor.connection.introspection.get_constraints(cursor, table_name)
    return index_name in constraints


def add_placement_points_column(apps, schema_editor):
    CategoryOverallResult = apps.get_model("kb_live", "CategoryOverallResult")
    table_name = CategoryOverallResult._meta.db_table
    if _column_exists(schema_editor, table_name, FIELD_NAME):
        return
    field = models.FloatField(
        verbose_name="Suma punktów z miejsc",
        null=True,
        blank=True,
        db_index=True,
    )
    field.set_attributes_from_name(FIELD_NAME)
    schema_editor.add_field(CategoryOverallResult, field)


def remove_placement_points_column(apps, schema_editor):
    CategoryOverallResult = apps.get_model("kb_live", "CategoryOverallResult")
    table_name = CategoryOverallResult._meta.db_table
    if not _column_exists(schema_editor, table_name, FIELD_NAME):
        return
    field = models.FloatField(
        verbose_name="Suma punktów z miejsc",
        null=True,
        blank=True,
        db_index=True,
    )
    field.set_attributes_from_name(FIELD_NAME)
    try:
        schema_editor.remove_field(CategoryOverallResult, field)
    except Exception:
        # Some backends (e.g. SQLite < 3.35) do not support dropping columns.
        pass


def add_category_placement_index(apps, schema_editor):
    CategoryOverallResult = apps.get_model("kb_live", "CategoryOverallResult")
    table_name = CategoryOverallResult._meta.db_table
    if not _column_exists(schema_editor, table_name, FIELD_NAME):
        return
    if _index_exists(schema_editor, table_name, INDEX_NAME):
        return
    index = models.Index(fields=["category", FIELD_NAME], name=INDEX_NAME)
    try:
        schema_editor.add_index(CategoryOverallResult, index)
    except Exception:
        # Ignore if backend cannot create the index for any reason.
        pass


def remove_category_placement_index(apps, schema_editor):
    CategoryOverallResult = apps.get_model("kb_live", "CategoryOverallResult")
    table_name = CategoryOverallResult._meta.db_table
    if not _index_exists(schema_editor, table_name, INDEX_NAME):
        return
    index = models.Index(fields=["category", FIELD_NAME], name=INDEX_NAME)
    try:
        schema_editor.remove_index(CategoryOverallResult, index)
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("kb_live", "0008_ensure_category_max_counted_disciplines"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="categoryoverallresult",
                    name=FIELD_NAME,
                    field=models.FloatField(
                        verbose_name="Suma punktów z miejsc",
                        null=True,
                        blank=True,
                        db_index=True,
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(add_placement_points_column, remove_placement_points_column),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterModelOptions(
                    name="categoryoverallresult",
                    options={
                        "verbose_name": "Wynik Ogólny Kategorii",
                        "verbose_name_plural": "Wyniki Ogólne Kategorii",
                        "unique_together": {("player", "category")},
                        "ordering": ["category", "final_position", "placement_points", "-total_points"],
                        "indexes": [
                            models.Index(fields=["category", "final_position"], name="kb_live_cat_categor_4a3253_idx"),
                            models.Index(fields=["category", FIELD_NAME], name=INDEX_NAME),
                            models.Index(fields=["category", "total_points"], name="kb_live_cat_categor_d86cfc_idx"),
                            models.Index(fields=["player", "category"], name="kb_live_cat_player__204779_idx"),
                        ],
                    },
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[
                migrations.RunPython(add_category_placement_index, remove_category_placement_index),
            ],
        ),
    ]
