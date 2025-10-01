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


class CachedForeignKeyWidget(ForeignKeyWidget):
    """Caches lookups and creates missing related objects once per import."""

    def __init__(self, *args, cache=None, normalizer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = cache if cache is not None else {}
        self.normalizer = normalizer or (lambda v: v)

    def clean(self, value, row=None, *args, **kwargs):
        normalized = self.normalizer(value)
        if not normalized:
            return None
        cached = self.cache.get(normalized)
        if cached is not None:
            return cached
        # fall back to DB lookup and cache the result
        obj = self.model.objects.filter(**{self.field: normalized}).first()
        if obj is None:
            obj = self.model.objects.create(**{self.field: normalized})
        self.cache[normalized] = obj
        return obj


class CachedManyToManyWidget(ManyToManyWidget):
    """Caches ManyToMany lookups to reduce query load during imports."""

    def __init__(self, *args, cache=None, normalizer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = cache if cache is not None else {}
        self.normalizer = normalizer or (lambda v: v)

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []
        if isinstance(value, str):
            raw_values = value.split(self.separator)
        else:
            raw_values = value
        instances = []
        for item in raw_values:
            normalized = self.normalizer(item)
            if not normalized:
                continue
            cached = self.cache.get(normalized)
            if cached is None:
                cached = self.model.objects.filter(**{self.field: normalized}).first()
                if cached is None:
                    cached = self.model.objects.create(**{self.field: normalized})
                self.cache[normalized] = cached
            instances.append(cached)
        return instances

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
    def __init__(self, *args, **kwargs):
        # Django-import-export passes request/form via kwargs; store them for potential future use
        self.request = kwargs.pop("request", None)
        self.form = kwargs.pop("form", None)
        super().__init__(*args, **kwargs)
        self._club_cache = {}
        self._category_cache = {}
        normalizer = self._normalize_value
        self.fields["club"].widget = CachedForeignKeyWidget(
            model=SportClub,
            field="name",
            cache=self._club_cache,
            normalizer=normalizer,
        )
        self.fields["categories"].widget = CachedManyToManyWidget(
            model=Category,
            separator=",",
            field="name",
            cache=self._category_cache,
            normalizer=normalizer,
        )

    @staticmethod
    def _normalize_value(value):
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return str(value).strip()

    def _collect_unique_related_values(self, dataset):
        club_names = set()
        category_names = set()
        rows = getattr(dataset, "dict", None)
        if callable(rows):
            rows = rows()
        if rows is None:
            rows = dataset
        for row in rows:
            club_name = self._normalize_value(row.get("club"))
            if club_name:
                club_names.add(club_name)
            for category in self._split_categories(row.get("categories")):
                category_names.add(category)
        return club_names, category_names

    def before_import(self, dataset, using_transactions=None, dry_run=None, **kwargs):
        super().before_import(
            dataset,
            using_transactions=using_transactions,
            dry_run=dry_run,
            **kwargs,
        )
        club_names, category_names = self._collect_unique_related_values(dataset)
        if club_names:
            existing = SportClub.objects.in_bulk(club_names, field_name="name")
            self._club_cache.update(existing)
            missing = [SportClub(name=name) for name in club_names if name not in existing]
            if missing:
                SportClub.objects.bulk_create(missing, ignore_conflicts=True)
                self._club_cache.update(
                    SportClub.objects.in_bulk(club_names, field_name="name")
                )
        if category_names:
            existing = Category.objects.in_bulk(category_names, field_name="name")
            self._category_cache.update(existing)
            missing = [Category(name=name) for name in category_names if name not in existing]
            if missing:
                Category.objects.bulk_create(missing, ignore_conflicts=True)
                self._category_cache.update(
                    Category.objects.in_bulk(category_names, field_name="name")
                )

    def _split_categories(self, value):
        if not value:
            return []
        if isinstance(value, str):
            raw_values = value.split(",")
        else:
            raw_values = value
        seen = set()
        cleaned = []
        for item in raw_values:
            normalized = self._normalize_value(item)
            if normalized and normalized not in seen:
                seen.add(normalized)
                cleaned.append(normalized)
        return cleaned

    def before_import_row(self, row, row_number=None, **kwargs):
        club_name = self._normalize_value(row.get("club"))
        row["club"] = club_name
        categories = self._split_categories(row.get("categories"))
        separator = self.fields["categories"].widget.separator
        row["categories"] = separator.join(categories)

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
