from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .choices import Discipline


class PlayerCategoryParticipation(models.Model):
    """
    Udział zawodnika w konkurencjach w ramach danej kategorii.

    - Rekord istnieje dla (player, category), gdzie zawodnik jest przypisany do kategorii.
    - Flagi bool określają, czy dana konkurencja ma być liczona „normalnie” (True),
      czy też zawodnik dostaje aktualnie ostatnie miejsce w tej konkurencji (False).
    - Jeśli kategoria nie zawiera danej konkurencji, flaga jest ignorowana.
    - Domyślnie wszystkie są zaznaczone (True), aby zachować dotychczasowe działanie.
    """

    player = models.ForeignKey(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="category_participations",
    )
    category = models.ForeignKey(
        "kb_live.Category",
        on_delete=models.CASCADE,
        verbose_name=_("Kategoria"),
        related_name="participations",
    )

    # Flagi udziału per konkurencja
    snatch = models.BooleanField(_(Discipline.SNATCH.label), default=True)
    tgu = models.BooleanField(_(Discipline.TGU.label), default=True)
    squat = models.BooleanField(_(Discipline.SQUAT.label), default=True)
    see_saw_press = models.BooleanField(_(Discipline.SEE_SAW_PRESS.label), default=True)
    pistol = models.BooleanField(_(Discipline.PISTOL.label), default=True)
    pull_up = models.BooleanField(_(Discipline.PULL_UP.label), default=True)

    class Meta:
        verbose_name = _("Udział Zawodnika w Konkurencjach (Kategoria)")
        verbose_name_plural = _("Udziały Zawodników w Konkurencjach (Kategoria)")
        unique_together = ("player", "category")
        ordering = ["player__surname", "player__name", "category__name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["player"]),
        ]

    def __str__(self) -> str:
        return f"{self.player} · {self.category} — udział w konkurencjach"

    def as_map(self) -> dict[str, bool]:
        """Zwraca mapę {discipline_code: bool} dla wszystkich konkurencji."""
        return {
            Discipline.SNATCH: bool(self.snatch),
            Discipline.TGU: bool(self.tgu),
            Discipline.SQUAT: bool(self.squat),
            Discipline.SEE_SAW_PRESS: bool(self.see_saw_press),
            Discipline.PISTOL: bool(self.pistol),
            Discipline.PULL_UP: bool(self.pull_up),
        }

