from django.db import models
from django.utils.translation import gettext_lazy as _


class PlayerCategoryTiebreak(models.Model):
    """
    Obecność rekordu oznacza: dodaj +1.0 pkt zawodnikowi w danej kategorii
    (wpływa na CategoryPlacement.points).
    """

    player = models.ForeignKey(
        "live_results.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="tiebreaks_applied",
    )
    category = models.ForeignKey(
        "live_results.Category",
        on_delete=models.CASCADE,
        verbose_name=_("Kategoria"),
        related_name="tiebreaks_applied",
    )

    class Meta:
        verbose_name = _("Zastosowany Tiebreak (Zawodnik-Kategoria)")
        verbose_name_plural = _("Zastosowane Tiebreaki (Zawodnik-Kategoria)")
        unique_together = ("player", "category")
        ordering = ["player__surname", "player__name", "category__name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["player"]),
        ]

    def __str__(self):
        return f"Tiebreak: {self.player} w kat. {self.category}"
