from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from kb_live.models import Category, CategoryOverallResult, Discipline, Player
from kb_live.services.ranking import rank_category_disciplines, rank_category_overall


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

        rows = list(
            category.placements.filter(discipline=disc).select_related("player", "category")
        )

        with transaction.atomic():
            affected_players = rank_category_disciplines(category.pk, disciplines=[disc])
            player_ids = {r.player_id for r in rows if r.player_id} | affected_players
            if player_ids:
                player_lookup = {
                    p.pk: p for p in Player.objects.filter(pk__in=player_ids)
                }
                existing_overalls = {
                    obj.player_id: obj
                    for obj in CategoryOverallResult.objects.filter(
                        category=category, player_id__in=player_ids
                    ).select_related("player", "category")
                }

                for player_id in player_ids:
                    player = player_lookup.get(player_id)
                    if player is None:
                        continue
                    overall = existing_overalls.get(player_id)
                    if overall is None:
                        overall, _ = CategoryOverallResult.objects.get_or_create(player=player, category=category)
                        existing_overalls[player_id] = overall
                    else:
                        overall.player = player
                        overall.category = category
                    overall.recompute(save=True)

            # Po zmianach miejsc w tej konkurencji warto przeliczyć wyniki overall
            rank_category_overall(category.pk, recompute_disciplines=False)

        self.stdout.write(
            self.style.SUCCESS(f"Nadano miejsca: kategoria='{category.name}', konkurencja='{disc}', n={len(rows)}")
        )
