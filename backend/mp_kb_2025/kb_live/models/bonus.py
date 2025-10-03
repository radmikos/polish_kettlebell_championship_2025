from django.db import models
from django.utils.translation import gettext_lazy as _


class PlayerCategoryBonus(models.Model):
    """Custom bonus points assigned to a player within a category."""

    player = models.ForeignKey(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="category_bonuses",
    )
    category = models.ForeignKey(
        "kb_live.Category",
        on_delete=models.CASCADE,
        verbose_name=_("Kategoria"),
        related_name="bonus_points_assigned",
    )
    points = models.FloatField(
        _("Dodatkowe punkty"),
        default=0.0,
        help_text=_("Liczba punktów doliczanych do klasyfikacji generalnej."),
    )

    class Meta:
        verbose_name = _("Dodatkowe punkty (Zawodnik-Kategoria)")
        verbose_name_plural = _("Dodatkowe punkty (Zawodnik-Kategoria)")
        unique_together = ("player", "category")
        ordering = ["player__surname", "player__name", "category__name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["player"]),
        ]

    def __str__(self) -> str:
        return f"Bonus: {self.player} w kat. {self.category} (+{self.points:g})"

