from django.core.management.base import BaseCommand, CommandError

from kb_live.models import Category, CategoryPlacement, Discipline


class Command(BaseCommand):
    help = "Nadaje miejsca w wybranej kategorii i konkurencji wg punktów (DESC)."

    def add_arguments(self, parser):
        parser.add_argument("category_id", type=int, help="ID kategorii")
        parser.add_argument("discipline", type=str, choices=[d for d, _ in Discipline.choices])

    def handle(self, *args, **opts):
        cat_id = opts["category_id"]
        disc = opts["discipline"]

        try:
            category = Category.objects.get(pk=cat_id)
        except Category.DoesNotExist:
            raise CommandError(f"Brak kategorii id={cat_id}")

        qs = CategoryPlacement.objects.filter(category=category, discipline=disc).select_related("player", "category")
        rows = list(qs)
        rows.sort(key=lambda r: (r.points or -1e18), reverse=True)

        for i, r in enumerate(rows, start=1):
            r.position = i if r.points is not None else None
        CategoryPlacement.objects.bulk_update(rows, ["position"])

        self.stdout.write(
            self.style.SUCCESS(f"Nadano miejsca: kategoria='{category.name}', konkurencja='{disc}', n={len(rows)}")
        )
