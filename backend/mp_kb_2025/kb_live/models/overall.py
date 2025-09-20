from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .category import Category
from .choices import Discipline
from .placement import CategoryPlacement
from .player import Player


class CategoryOverallResult(models.Model):
    """
    Syntetyczny wynik zawodnika w danej kategorii.

    Zmodyfikowana logika (sumowanie miejsc):
    1. Pola *_points przechowują SUROWE / ostatnio obliczone punkty z konkurencji.
       Jeśli konkurencja jest dozwolona w kategorii, ale brak wyniku – wpisywane jest 0.0 (żeby rekord był "widoczny").
       Jeśli konkurencja NIE jest dozwolona – pole = None.
    2. total_points = suma miejsc (position) z CategoryPlacement dla dozwolonych konkurencji.
       Jeśli brak miejsc => total_points = None (rekord istnieje, ale nie bierze udziału w rankingu).
    3. final_position ustalana osobno (ranking rosnąco po total_points).
    4. Niższa wartość total_points jest lepsza.
    """

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="category_results", verbose_name=_("Zawodnik")
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="overall_results", verbose_name=_("Kategoria")
    )

    snatch_points = models.FloatField(_("Punkty Snatch"), null=True, blank=True)
    tgu_points = models.FloatField(_("Punkty TGU"), null=True, blank=True)
    squat_points = models.FloatField(_("Punkty Squat"), null=True, blank=True)
    see_saw_press_points = models.FloatField(_("Punkty See-Saw"), null=True, blank=True)
    pistol_points = models.FloatField(_("Punkty Pistol"), null=True, blank=True)
    pull_up_points = models.FloatField(_("Punkty Pull-Up"), null=True, blank=True)

    tiebreak_points = models.FloatField(_("Punkty Tiebreak"), default=0.0)
    total_points = models.FloatField(_("Suma Miejsc"), null=True, blank=True, db_index=True)
    final_position = models.PositiveIntegerField(_("Miejsce Końcowe"), null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = _("Wynik Ogólny Kategorii")
        verbose_name_plural = _("Wyniki Ogólne Kategorii")
        unique_together = ("player", "category")
        ordering = ["category", "final_position", "total_points"]  # niższe total_points lepsze
        indexes = [
            models.Index(fields=["category", "final_position"]),
            models.Index(fields=["category", "total_points"]),
            models.Index(fields=["player", "category"]),
        ]

    def __str__(self) -> str:
        pos = self.final_position if self.final_position is not None else "N/A"
        pts = f"{self.total_points:.2f}" if self.total_points is not None else "N/A"
        return f"[{self.category}] {self.player} · Miejsce: {pos} · Suma miejsc: {pts}"

    def _is_allowed(self, key: str) -> bool:
        """Czy dana dyscyplina jest dozwolona w tej kategorii?"""
        return isinstance(self.category.disciplines, list) and key in self.category.disciplines

    def _points_map_from_player(self) -> dict[str, float | None]:
        """Zbiera punkty z globalnych wyników zawodnika (OneToOne), bez filtrowania po kategorii."""
        p = self.player
        return {
            Discipline.SNATCH: getattr(getattr(p, "snatch_result", None), "points", None),
            Discipline.TGU: getattr(getattr(p, "tgu_result", None), "points", None),
            Discipline.SQUAT: getattr(getattr(p, "squat_result", None), "points", None),
            Discipline.SEE_SAW_PRESS: getattr(getattr(p, "see_saw_press_result", None), "points", None),
            Discipline.PISTOL: getattr(getattr(p, "pistol_result", None), "points", None),
            Discipline.PULL_UP: getattr(getattr(p, "pull_up_result", None), "points", None),
        }

    def _placements_map(self) -> dict[str, int | None]:
        allowed = (
            [d for d in self.category.disciplines if isinstance(self.category.disciplines, list)]
            if isinstance(self.category.disciplines, list)
            else []
        )
        rows = CategoryPlacement.objects.filter(category=self.category, player=self.player, discipline__in=allowed)
        out: dict[str, int | None] = {d: None for d in allowed}
        for r in rows:
            out[r.discipline] = r.position
        return out

    def recompute(self, save: bool = True) -> None:
        # 1. Uaktualnij surowe punkty (dla podglądu) – tylko dla dozwolonych konkurencji.
        pts = self._points_map_from_player()

        def val_or_zero(key):
            if self._is_allowed(key):
                v = pts[key]
                return 0.0 if v is None else v
            return None

        self.snatch_points = val_or_zero(Discipline.SNATCH)
        self.tgu_points = val_or_zero(Discipline.TGU)
        self.squat_points = val_or_zero(Discipline.SQUAT)
        self.see_saw_press_points = val_or_zero(Discipline.SEE_SAW_PRESS)
        self.pistol_points = val_or_zero(Discipline.PISTOL)
        self.pull_up_points = val_or_zero(Discipline.PULL_UP)

        # 2. Tiebreak flag (nie dodajemy do sumy miejsc – może posłużyć do przyszłych tie-breaków)
        tb_exists = self.category.tiebreaks_applied.filter(player=self.player).exists()
        self.tiebreak_points = 1.0 if tb_exists else 0.0

        # 3. Suma miejsc (niższa lepsza) – brak miejsc => None (rekord na końcu klasyfikacji)
        placements = self._placements_map()
        place_values = [p for p in placements.values() if isinstance(p, int) and p > 0]
        self.total_points = float(sum(place_values)) if place_values else None

        if save:
            self.save(
                update_fields=[
                    "snatch_points",
                    "tgu_points",
                    "squat_points",
                    "see_saw_press_points",
                    "pistol_points",
                    "pull_up_points",
                    "tiebreak_points",
                    "total_points",
                ]
            )
