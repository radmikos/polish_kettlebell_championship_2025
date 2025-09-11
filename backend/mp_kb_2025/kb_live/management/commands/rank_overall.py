from django.core.management.base import BaseCommand
from itertools import groupby
from live_results.models import CategoryOverallResult, Category

class Command(BaseCommand):
    help = "Nadaje miejsca w overall na podstawie total_points (DESC)."

    def add_arguments(self, parser):
        parser.add_argument("--category", type=int, default=None, help="ID kategorii (opcjonalnie)")

    def handle(self, *args, **opts):
        cat_id = opts.get("category")
        qs = CategoryOverallResult.objects.select_related("category", "player")
        if cat_id:
            qs = qs.filter(category_id=cat_id)

        rows = list(qs)
        if cat_id:
            groups = [(cat_id, rows)]
        else:
            rows.sort(key=lambda r: r.category_id)
            groups = [(k, list(g)) for k, g in groupby(rows, key=lambda r: r.category_id)]

        total_updated = 0
        for _, group in groups:
            group.sort(key=lambda r: (r.total_points or -1e18), reverse=True)
            for i, r in enumerate(group, start=1):
                r.final_position = i if r.total_points is not None else None
            CategoryOverallResult.objects.bulk_update(group, ["final_position"])
            total_updated += len(group)

        self.stdout.write(self.style.SUCCESS(f"Nadano miejsca dla {total_updated} rekordów Overall."))
