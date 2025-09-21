from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from kb_live.models import Category, CategoryOverallResult, CategoryPlacement, Discipline
from kb_live.services.ranking import rank_category_overall


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

        with transaction.atomic():
            for i, r in enumerate(rows, start=1):
                r.position = i if r.points is not None else None
            CategoryPlacement.objects.bulk_update(rows, ["position"])

            player_map = {r.player_id: r.player for r in rows if r.player_id}
            if player_map:
                existing_overalls = {
                    obj.player_id: obj
                    for obj in CategoryOverallResult.objects.filter(
                        category=category, player_id__in=player_map.keys()
                    ).select_related("player", "category")
                }

                for player_id, player in player_map.items():
                    overall = existing_overalls.get(player_id)
                    if overall is None:
                        overall, _ = CategoryOverallResult.objects.get_or_create(player=player, category=category)
                        existing_overalls[player_id] = overall
                    else:
                        overall.player = player
                        overall.category = category
                    overall.recompute(save=True)

            rank_category_overall(category.pk)

        self.stdout.write(
            self.style.SUCCESS(f"Nadano miejsca: kategoria='{category.name}', konkurencja='{disc}', n={len(rows)}")
        )
