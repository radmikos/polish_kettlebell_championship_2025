from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from kb_live.models import (
    Player,
    CategoryOverallResult,
    SnatchResult,
    PistolResult,
    SeeSawPressResult,
    SquatResult,
    TGUResult,
    PullUpResult,
    Discipline,
)

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

@receiver(post_save, sender=Player)
def player_post_save_create_results(sender, instance: Player, created, **kwargs):
    if created:
        # categories may be empty now; discipline results will be created after categories added
        pass

@receiver(m2m_changed, sender=Player.categories.through)
def player_categories_changed(sender, instance: Player, action, reverse, pk_set, **kwargs):
    if action == "post_add":
        ensure_player_results(instance)
        ensure_overall_for_player_categories(instance, list(pk_set) if pk_set else None)
