from django.core.management.base import BaseCommand
from live_results.models import Category, CategoryOverallResult

class Command(BaseCommand):
    help = "Przelicza wyniki ogólne dla danej kategorii (lub wszystkich)."

    def add_arguments(self, parser):
        parser.add_argument("--category", type=int, default=None, help="ID kategorii (opcjonalnie)")

    def handle(self, *args, **opts):
        cat_id = opts.get("category")
        qs = CategoryOverallResult.objects.all().select_related("player", "category")
        if cat_id:
            qs = qs.filter(category_id=cat_id)
        n = 0
        for r in qs:
            r.recompute(save=True)
            n += 1
        self.stdout.write(self.style.SUCCESS(f"Przeliczono {n} rekordów Overall."))
