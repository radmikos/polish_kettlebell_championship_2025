from __future__ import annotations
from typing import Optional, Dict

from django.db import models
from django.utils.translation import gettext_lazy as _
from .player import Player
from .category import Category
from .choices import Discipline

class CategoryOverallResult(models.Model):
    """
    Syntetyczny wynik zawodnika w danej kategorii:
    - zbiera punkty z DOZWOLONYCH w kategorii dyscyplin
    - dolicza tiebreak (+1) jeśli istnieje wpis PlayerCategoryTiebreak
    - przechowuje total + final_position do szybkich rankingów/eksportów
    """
    player   = models.ForeignKey(Player,   on_delete=models.CASCADE, related_name="category_results",   verbose_name=_("Zawodnik"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="overall_results",    verbose_name=_("Kategoria"))

    # Pola podglądowe (None gdy brak wyniku / konkurencja niedozwolona w kat.)
    snatch_points       = models.FloatField(_("Punkty Snatch"),      null=True, blank=True)
    tgu_points          = models.FloatField(_("Punkty TGU"),         null=True, blank=True)
    squat_points        = models.FloatField(_("Punkty Squat"),       null=True, blank=True)           # 2xKB suma
    see_saw_press_points= models.FloatField(_("Punkty See-Saw"),     null=True, blank=True)           # 2xKB suma
    pistol_points       = models.FloatField(_("Punkty Pistol"),      null=True, blank=True)
    pull_up_points      = models.FloatField(_("Punkty Pull-Up"),     null=True, blank=True)

    tiebreak_points = models.FloatField(_("Punkty Tiebreak"), default=0.0)  # zwykle 0 lub 1.0
    total_points    = models.FloatField(_("Suma Punktów"),    null=True, blank=True, db_index=True)
    final_position  = models.PositiveIntegerField(_("Miejsce Końcowe"), null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = _("Wynik Ogólny Kategorii")
        verbose_name_plural = _("Wyniki Ogólne Kategorii")
        unique_together = ("player", "category")
        ordering = ["category", "final_position", "-total_points"]
        indexes = [
            models.Index(fields=["category", "final_position"]),
            models.Index(fields=["category", "total_points"]),
            models.Index(fields=["player", "category"]),
        ]

    def __str__(self) -> str:
        pos = self.final_position if self.final_position is not None else "N/A"
        pts = f"{self.total_points:.2f}" if self.total_points is not None else "N/A"
        return f"[{self.category}] {self.player} · Miejsce: {pos} · Punkty: {pts}"

    # --- API obliczeń ---

    def _is_allowed(self, key: str) -> bool:
        """Czy dana dyscyplina jest dozwolona w tej kategorii?"""
        return isinstance(self.category.disciplines, list) and key in self.category.disciplines

    def _points_map_from_player(self) -> Dict[str, Optional[float]]:
        """Zbiera punkty z globalnych wyników zawodnika (OneToOne), bez filtrowania po kategorii."""
        p = self.player
        return {
            Discipline.SNATCH:        getattr(getattr(p, "snatch_result", None), "points", None),
            Discipline.TGU:           getattr(getattr(p, "tgu_result", None), "points", None),
            Discipline.SQUAT:         getattr(getattr(p, "squat_result", None), "points", None),
            Discipline.SEE_SAW_PRESS: getattr(getattr(p, "see_saw_press_result", None), "points", None),
            Discipline.PISTOL:        getattr(getattr(p, "pistol_result", None), "points", None),
            Discipline.PULL_UP:       getattr(getattr(p, "pull_up_result", None), "points", None),
        }

    def recompute(self, save: bool = True) -> None:
        """
        Przelicza pola *_points tylko dla konkurencji DOZWOLONYCH w kategorii,
        dolicza tiebreak (+1), liczy total i opcjonalnie zapisuje.
        """
        pts = self._points_map_from_player()

        # wypełnij pola per dyscyplina tylko gdy dozwolone w kategorii
        self.snatch_points        = pts[Discipline.SNATCH]        if self._is_allowed(Discipline.SNATCH)        else None
        self.tgu_points           = pts[Discipline.TGU]           if self._is_allowed(Discipline.TGU)           else None
        self.squat_points         = pts[Discipline.SQUAT]         if self._is_allowed(Discipline.SQUAT)         else None
        self.see_saw_press_points = pts[Discipline.SEE_SAW_PRESS] if self._is_allowed(Discipline.SEE_SAW_PRESS) else None
        self.pistol_points        = pts[Discipline.PISTOL]        if self._is_allowed(Discipline.PISTOL)        else None
        self.pull_up_points       = pts[Discipline.PULL_UP]       if self._is_allowed(Discipline.PULL_UP)       else None

        # tiebreak +1 jeśli istnieje wpis PlayerCategoryTiebreak
        tb_exists = self.category.tiebreaks_applied.filter(player=self.player).exists()
        self.tiebreak_points = 1.0 if tb_exists else 0.0

        # suma
        parts = [
            self.snatch_points, self.tgu_points, self.squat_points,
            self.see_saw_press_points, self.pistol_points, self.pull_up_points,
        ]
        valid = [x for x in parts if isinstance(x, (int, float))]
        self.total_points = (sum(valid) + self.tiebreak_points) if valid else None

        if save:
            self.save(update_fields=[
                "snatch_points", "tgu_points", "squat_points", "see_saw_press_points",
                "pistol_points", "pull_up_points", "tiebreak_points", "total_points"
            ])
