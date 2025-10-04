from django.db import models
from django.utils.translation import gettext_lazy as _

from .category import Category
from .choices import Discipline
from .bonus import get_player_bonus_share
from .player import Player


class CategoryPlacement(models.Model):
    """
    Pozycja zawodnika w KATEGORII dla KONKURENCJI,
    liczona na podstawie JEDNEGO globalnego wyniku oraz kary tiebreak (-0.5) dla (player, category).
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_("Kategoria"),
        related_name="placements",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="placements",
    )
    discipline = models.CharField(
        _("Konkurencja"),
        max_length=32,
        choices=Discipline.choices,
    )
    position = models.PositiveIntegerField(_("Miejsce"), null=True, blank=True)

    class Meta:
        verbose_name = _("Miejsce w kategorii")
        verbose_name_plural = _("Miejsca w kategoriach")
        ordering = ["category", "discipline", "position", "player_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "discipline", "player"],
                name="uniq_category_discipline_player",
            ),
        ]
        indexes = [
            models.Index(fields=["category", "discipline", "position"]),
            models.Index(fields=["discipline", "player"]),
        ]

    def __str__(self) -> str:
        return f"{self.category} · {self.get_discipline_display()} · {self.player} · pos={self.position or '-'}"

    # --- punkty bez dogrywki ---
    @property
    def base_points(self) -> float | None:
        p = self.player
        d = self.discipline
        try:
            if d == Discipline.SNATCH:
                return p.snatch_result.points
            if d == Discipline.PISTOL:
                return p.pistol_result.points
            if d == Discipline.SEE_SAW_PRESS:
                return p.see_saw_press_result.points
            if d == Discipline.SQUAT:
                return p.squat_result.points
            if d == Discipline.TGU:
                return p.tgu_result.points
            if d == Discipline.PULL_UP:
                return p.pull_up_result.points
        except AttributeError:
            return None
        return None

    # --- punkty z uwzględnioną karą tiebreak (-0.5) ---
    @property
    def points(self) -> float:
        base = self.base_points
        base_value = float(base) if base is not None else 0.0
        _general_bonus, discipline_bonuses = get_player_bonus_share(self.category, self.player_id)
        bonus_value = discipline_bonuses.get(self.discipline, 0.0)
        total = base_value + bonus_value
        if self.category.tiebreaks_applied.filter(player=self.player).exists():
            total -= 0.5
        return total
