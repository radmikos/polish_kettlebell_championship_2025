from itertools import groupby

from django.core.management.base import BaseCommand

from kb_live.models import CategoryOverallResult
from kb_live.services.ranking import rank_category_overall

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
        for cat_id, group in groups:
            for row in group:
                row.recompute(save=True)
            total_updated += rank_category_overall(cat_id)

        self.stdout.write(self.style.SUCCESS(f"Przeliczono i nadano miejsca (overall) dla {total_updated} rekordów."))
