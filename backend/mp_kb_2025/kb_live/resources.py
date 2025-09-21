from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget, Widget

from .models.player import Player
from .models.category import Category
from .models.sports_club import SportClub

class GenderPolishWidget(Widget):
    def clean(self, value, row=None, *args, **kwargs):
        value = (value or "").strip().capitalize()
        if value in ["Kobieta", "Mężczyzna"]:
            return value
        # fallback: try to map English to Polish
        if value.lower() == "female":
            return "Kobieta"
        if value.lower() == "male":
            return "Mężczyzna"
        return ""
    def render(self, value, obj=None):
        return value if value else ""

class PlayerResource(resources.ModelResource):
    club = fields.Field(
        column_name="club",
        attribute="club",
        widget=ForeignKeyWidget(model=SportClub, field="name")
    )
    categories = fields.Field(
        column_name="categories",
        attribute="categories",
        widget=ManyToManyWidget(model=Category, separator=",", field="name"),
    )
    gender = fields.Field(
        column_name="gender",
        attribute="gender",
        widget=GenderPolishWidget(),
    )
    class Meta:
        model = Player
        fields = ("id", "name", "surname", "weight", "gender", "club", "categories")
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("id",)

class PlayerImportResource(PlayerResource):
    def before_import_row(self, row, row_number=None, **kwargs):
        club_name = row.get("club")
        if club_name:
            club, _ = SportClub.objects.get_or_create(name=club_name.strip())
        categories_str = row.get("categories")
        if categories_str:
            category_names = [name.strip() for name in categories_str.split(",") if name.strip()]
            for cat_name in category_names:
                Category.objects.get_or_create(name=cat_name)
    def skip_row(self, instance, original, row, import_validation_errors=None):
        is_new_instance = instance.pk is None
        if is_new_instance:
            name = row.get("name", "").strip()
            surname = row.get("surname", "").strip()
            if name and surname:
                exists = Player.objects.filter(name__iexact=name, surname__iexact=surname).exists()
                if exists:
                    return True
        return super().skip_row(instance, original, row, import_validation_errors)
    def after_save_instance(self, instance: Player, row, **kwargs):
        dry_run = kwargs.get('dry_run', False)
        if not dry_run:
            instance.refresh_from_db()
            db_cats = list(instance.categories.all())
            category_pks = set(c.pk for c in db_cats)

class PlayerExportResource(PlayerResource):
    pass
