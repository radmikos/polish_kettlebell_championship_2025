from collections.abc import Iterable

from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from kb_live.models import (
    CategoryOverallResult,
    CategoryPlacement,
    Discipline,
    PistolResult,
    Player,
    PlayerCategoryTiebreak,
    PullUpResult,
    SeeSawPressResult,
    SnatchResult,
    SquatResult,
    TGUResult,
)
from kb_live.services.ranking import rank_category_overall

DISCIPLINE_MODEL_MAP = {
    Discipline.SNATCH: SnatchResult,
    Discipline.PISTOL: PistolResult,
    Discipline.SEE_SAW_PRESS: SeeSawPressResult,
    Discipline.SQUAT: SquatResult,
    Discipline.TGU: TGUResult,
    Discipline.PULL_UP: PullUpResult,
}


def _allowed_discipline_codes(player: Player) -> set[str]:
    codes: set[str] = set()
    for cat in player.categories.all():
        if isinstance(cat.disciplines, list):
            codes.update(cat.disciplines)
    return codes


def ensure_player_results(player: Player):
    allowed = _allowed_discipline_codes(player)
    if not allowed:
        return  # brak kategorii => nic nie tworzymy teraz
    for code, model in DISCIPLINE_MODEL_MAP.items():
        if code in allowed:
            model.objects.get_or_create(player=player)


def ensure_overall_for_player_categories(player: Player, category_ids: list[int] | None = None):
    qs = player.categories.all()
    if category_ids is not None:
        qs = qs.filter(id__in=category_ids)
    for cat in qs:
        obj, created = CategoryOverallResult.objects.get_or_create(player=player, category=cat)
        obj.recompute(save=True)


def cleanup_player_results(player: Player, category_ids: Iterable[int] | None = None) -> set[int]:
    filter_kwargs = {"player": player}
    if category_ids is not None:
        ids = list(category_ids)
        if not ids:
            return set()
        filter_kwargs["category_id__in"] = ids

    qs_overall = CategoryOverallResult.objects.filter(**filter_kwargs)
    affected_categories = set(qs_overall.values_list("category_id", flat=True))
    qs_overall.delete()
    CategoryPlacement.objects.filter(**filter_kwargs).delete()
    PlayerCategoryTiebreak.objects.filter(**filter_kwargs).delete()

    remaining_allowed = _allowed_discipline_codes(player)
    for code, model in DISCIPLINE_MODEL_MAP.items():
        if code not in remaining_allowed:
            model.objects.filter(player=player).delete()

    return affected_categories


def _schedule_overall_refresh(category_id: int, player_ids: Iterable[int] | None = None) -> None:
    if not category_id:
        return

    player_ids_set = {pid for pid in (player_ids or []) if pid}

    def _run():
        if player_ids_set:
            players = Player.objects.filter(pk__in=player_ids_set)
            for player in players:
                ensure_overall_for_player_categories(player, [category_id])
        rank_category_overall(category_id)

    transaction.on_commit(_run)



# --- DODAJ SYGNAŁY DLA WYNIKÓW DYSCYPLIN ---
@receiver(post_save, sender=SnatchResult)
@receiver(post_save, sender=TGUResult)
@receiver(post_save, sender=SquatResult)
@receiver(post_save, sender=SeeSawPressResult)
@receiver(post_save, sender=PistolResult)
@receiver(post_save, sender=PullUpResult)
def discipline_result_saved(sender, instance, **kwargs):
    player = instance.player
    # Upewnij się, że overall jest przeliczony dla wszystkich kategorii zawodnika
    ensure_overall_for_player_categories(player)


@receiver(m2m_changed, sender=Player.categories.through)
def player_categories_changed(sender, instance: Player, action, reverse, pk_set, **kwargs):
    if reverse:
        return

    if action == "post_add":
        ensure_player_results(instance)
        ensure_overall_for_player_categories(instance, list(pk_set) if pk_set else None)
        for cat_id in (pk_set or []):
            _schedule_overall_refresh(cat_id, [instance.pk])
    elif action == "post_remove":
        cat_ids = list(pk_set) if pk_set else []
        affected = cleanup_player_results(instance, cat_ids)
        for cat_id in affected:
            _schedule_overall_refresh(cat_id)
    elif action == "post_clear":
        affected = cleanup_player_results(instance, None)
        for cat_id in affected:
            _schedule_overall_refresh(cat_id)


@receiver(post_save, sender=CategoryPlacement)
def category_placement_saved(sender, instance: CategoryPlacement, **kwargs):
    if kwargs.get("raw"):
        return
    _schedule_overall_refresh(instance.category_id, [instance.player_id])


@receiver(post_delete, sender=CategoryPlacement)
def category_placement_deleted(sender, instance: CategoryPlacement, **kwargs):
    _schedule_overall_refresh(instance.category_id, [instance.player_id])


@receiver(post_save, sender=PlayerCategoryTiebreak)
def tiebreak_saved(sender, instance: PlayerCategoryTiebreak, **kwargs):
    if kwargs.get("raw"):
        return
    _schedule_overall_refresh(instance.category_id, [instance.player_id])


@receiver(post_delete, sender=PlayerCategoryTiebreak)
def tiebreak_deleted(sender, instance: PlayerCategoryTiebreak, **kwargs):
    _schedule_overall_refresh(instance.category_id, [instance.player_id])
