from django.core.management.base import BaseCommand
from itertools import groupby
from kb_live.models import CategoryOverallResult

class Command(BaseCommand):
    help = "Nadaje miejsca w overall na podstawie sumy miejsc (ASC – mniej lepsze)."

    def add_arguments(self, parser):
        parser.add_argument("--category", type=int, default=None, help="ID kategorii (opcjonalnie)")

    def handle(self, *args, **opts):
        cat_id = opts.get("category")
        qs = CategoryOverallResult.objects.select_related("category", "player")
        if cat_id:
            qs = qs.filter(category_id=cat_id)

        rows = list(qs)
        if not rows:
            self.stdout.write(self.style.WARNING("Brak rekordów do rankingu."))
            return

        if cat_id:
            groups = [(cat_id, rows)]
        else:
            rows.sort(key=lambda r: r.category_id)
            groups = [(k, list(g)) for k, g in groupby(rows, key=lambda r: r.category_id)]

        total_updated = 0
        for _, group in groups:
            # Ascending: None last
            group.sort(key=lambda r: (r.total_points is None, r.total_points, getattr(r.player, 'surname', ''), getattr(r.player, 'name', '')))
            for i, r in enumerate(group, start=1):
                r.final_position = i if r.total_points is not None else None
            CategoryOverallResult.objects.bulk_update(group, ["final_position"])
            total_updated += len(group)

        self.stdout.write(self.style.SUCCESS(f"Nadano miejsca (overall) dla {total_updated} rekordów."))
