
from django.db import migrations, models


OLD_INDEX = "kb_live_cat_categor_0d5b6a_idx"
NEW_INDEX = "kb_live_cat_categor_168d8b_idx"


def _get_constraints(schema_editor, table_name):
    with schema_editor.connection.cursor() as cursor:
        return schema_editor.connection.introspection.get_constraints(cursor, table_name)


def _index(fields, name):
    return models.Index(fields=fields, name=name)


def _ensure_index(model, schema_editor, source, target):
    table_name = model._meta.db_table
    constraints = _get_constraints(schema_editor, table_name)
    has_source = source in constraints
    has_target = target in constraints

    if has_source and not has_target:
        try:
            schema_editor.rename_index(
                model,
                _index(["category", "placement_points"], source),
                _index(["category", "placement_points"], target),
            )
            return
        except NotImplementedError:
            pass
        # Fallback: create target index, then drop the source one.
        target_index = _index(["category", "placement_points"], target)
        schema_editor.add_index(model, target_index)
        try:
            schema_editor.remove_index(model, _index(["category", "placement_points"], source))
        except Exception:
            # Ignore if backend already removed it or doesn't support DROP INDEX.
            pass
        return

    if not has_source and not has_target:
        schema_editor.add_index(model, _index(["category", "placement_points"], target))


def forwards(apps, schema_editor):
    Model = apps.get_model("kb_live", "CategoryOverallResult")
    _ensure_index(Model, schema_editor, OLD_INDEX, NEW_INDEX)


def backwards(apps, schema_editor):
    Model = apps.get_model("kb_live", "CategoryOverallResult")
    _ensure_index(Model, schema_editor, NEW_INDEX, OLD_INDEX)


class Migration(migrations.Migration):

    dependencies = [
        ("kb_live", "0010_categoryoverallresult_places"),
    ]

    operations = [
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
                            models.Index(fields=["category", "placement_points"], name=NEW_INDEX),
                            models.Index(fields=["category", "total_points"], name="kb_live_cat_categor_d86cfc_idx"),
                            models.Index(fields=["player", "category"], name="kb_live_cat_player__204779_idx"),
                        ],
                    },
                ),
            ],
            database_operations=[
                migrations.RunPython(forwards, backwards),
            ],
        ),
        migrations.AlterField(
            model_name="categoryoverallresult",
            name="total_points",
            field=models.FloatField(blank=True, db_index=True, null=True, verbose_name="Suma punktów"),
        ),
    ]
