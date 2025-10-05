from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .category import Category
from .choices import Discipline
from .placement import CategoryPlacement
from .player import Player
from .participation import PlayerCategoryParticipation


class CategoryOverallResult(models.Model):
    """
    Syntetyczny wynik zawodnika w danej kategorii.

    Logika przeliczeń:
    1. Pola *_points przechowują surowe, ostatnio obliczone punkty z konkurencji.
       Jeśli konkurencja jest dozwolona, ale brak wyniku – zapisujemy 0.0.
       Jeśli konkurencja NIE jest dozwolona – pole pozostaje puste (None).
    2. total_points = suma punktów z dozwolonych konkurencji (najwyższa wartość lepsza).
       Jeśli kategoria ma limit punktowanych wyników – bierzemy najwyższe punkty.
    3. placement_points = suma miejsc z CategoryPlacement (najniższa wartość lepsza).
       Przy limicie konkurencji bierzemy najlepsze (najniższe) miejsca.
    4. final_position ustalana rosnąco po placement_points.
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

    snatch_place = models.PositiveIntegerField(_("Miejsce Snatch"), null=True, blank=True)
    tgu_place = models.PositiveIntegerField(_("Miejsce TGU"), null=True, blank=True)
    squat_place = models.PositiveIntegerField(_("Miejsce Squat"), null=True, blank=True)
    see_saw_press_place = models.PositiveIntegerField(_("Miejsce See-Saw"), null=True, blank=True)
    pistol_place = models.PositiveIntegerField(_("Miejsce Pistol"), null=True, blank=True)
    pull_up_place = models.PositiveIntegerField(_("Miejsce Pull-Up"), null=True, blank=True)

    tiebreak_points = models.FloatField(_("Punkty Tiebreak"), default=0.0)
    bonus_points = models.FloatField(
        _("Punkty dodatkowe"),
        default=0.0,
        help_text=_("Suma dodatkowych punktów przyznanych ręcznie w klasyfikacji generalnej."),
    )
    total_points = models.FloatField(_("Suma punktów"), null=True, blank=True, db_index=True)
    placement_points = models.FloatField(_("Suma punktów z miejsc"), null=True, blank=True, db_index=True)
    counted_disciplines = models.PositiveSmallIntegerField(
        _("Liczba zaliczonych konkurencji"),
        default=0,
        help_text=_("Ile wyników wliczono do sumy miejsc w danym przeliczeniu."),
    )
    final_position = models.PositiveIntegerField(_("Miejsce Końcowe"), null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = _("Wynik Ogólny Kategorii")
        verbose_name_plural = _("Wyniki Ogólne Kategorii")
        unique_together = ("player", "category")
        ordering = ["category", "final_position", "placement_points", "-total_points"]
        indexes = [
            models.Index(fields=["category", "final_position"]),
            models.Index(fields=["category", "placement_points"]),
            models.Index(fields=["category", "total_points"]),
            models.Index(fields=["player", "category"]),
        ]

    def __str__(self) -> str:
        pos = self.final_position if self.final_position is not None else "N/A"
        placement = f"{self.placement_points:.2f}" if self.placement_points is not None else "N/A"
        total = f"{self.total_points:.2f}" if self.total_points is not None else "N/A"
        return f"[{self.category}] {self.player} · Miejsce: {pos} · Suma miejsc: {placement} · Suma pkt: {total}"

    def _allowed_disciplines(self) -> list[str]:
        discs = getattr(self.category, "disciplines", None)
        if isinstance(discs, list):
            return [d for d in discs if isinstance(d, str)]
        return []

    def _is_allowed(self, key: str) -> bool:
        """Czy dana dyscyplina jest dozwolona w tej kategorii?"""
        return key in self._allowed_disciplines()

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
        allowed = self._allowed_disciplines()
        rows = CategoryPlacement.objects.filter(category=self.category, player=self.player, discipline__in=allowed)
        out: dict[str, int | None] = {d: None for d in allowed}
        for r in rows:
            out[r.discipline] = r.position
        return out

    def _last_place_map(self) -> dict[str, int | None]:
        """Zwraca aktualnie najgorsze (najwyższe) miejsce w kategorii dla każdej konkurencji."""
        from django.db.models import Max

        allowed = self._allowed_disciplines()
        if not allowed:
            return {}

        qs = (
            CategoryPlacement.objects.filter(category=self.category, discipline__in=allowed)
            .values("discipline")
            .annotate(max_pos=Max("position"))
        )
        result: dict[str, int | None] = {code: None for code in allowed}
        for row in qs:
            result[str(row["discipline"])] = row["max_pos"]
        # Jeśli dla danej konkurencji nie istnieją jeszcze miejsca, przyjmij 1 jako „ostatnie”
        for code in allowed:
            if result.get(code) is None:
                result[code] = 1
        return result

    def recompute(self, save: bool = True) -> None:
        allowed_disciplines = self._allowed_disciplines()
        pts = self._points_map_from_player()
        allowed_set = set(allowed_disciplines)

        def normalized_points(key: str) -> float | None:
            if key not in allowed_set:
                return None
            value = pts.get(key)
            base = float(value) if value is not None else 0.0
            return base

        discipline_fields = [
            (Discipline.SNATCH, "snatch_points"),
            (Discipline.TGU, "tgu_points"),
            (Discipline.SQUAT, "squat_points"),
            (Discipline.SEE_SAW_PRESS, "see_saw_press_points"),
            (Discipline.PISTOL, "pistol_points"),
            (Discipline.PULL_UP, "pull_up_points"),
        ]

        aggregated_points: list[float] = []
        for code, attr_name in discipline_fields:
            value = normalized_points(code)
            setattr(self, attr_name, value)
            if value is not None:
                aggregated_points.append(float(value))

        # Kara tiebreak (odejmujemy 0.5 punktu od sumy końcowej)
        tb_exists = self.category.tiebreaks_applied.filter(player=self.player).exists()
        self.tiebreak_points = -0.5 if tb_exists else 0.0

        # Dodatkowe punkty wyłączone – zawsze 0.0
        self.bonus_points = 0.0

        drop_worst = bool(getattr(self.category, "drop_worst_result", False))

        placements = self._placements_map()
        last_places = self._last_place_map()

        # Udział zawodnika w konkurencjach w ramach kategorii (domyślnie wszystko True)
        participation = None
        try:
            participation = PlayerCategoryParticipation.objects.get(player=self.player, category=self.category)
            participation_map = participation.as_map()
        except PlayerCategoryParticipation.DoesNotExist:
            participation_map = {d: True for d in allowed_disciplines}

        place_fields = [
            (Discipline.SNATCH, "snatch_place"),
            (Discipline.TGU, "tgu_place"),
            (Discipline.SQUAT, "squat_place"),
            (Discipline.SEE_SAW_PRESS, "see_saw_press_place"),
            (Discipline.PISTOL, "pistol_place"),
            (Discipline.PULL_UP, "pull_up_place"),
        ]

        place_entries: list[tuple[str, int]] = []
        for code, attr_name in place_fields:
            effective_value: int | None = None
            if code in allowed_set:
                participate = participation_map.get(code, True)
                if participate:
                    value = placements.get(code)
                    if isinstance(value, int) and value > 0:
                        effective_value = value
                else:
                    # Nie bierze udziału → przypisz aktualnie ostatnie miejsce
                    effective_value = last_places.get(code)

            if isinstance(effective_value, int) and effective_value > 0:
                setattr(self, attr_name, effective_value)
                place_entries.append((code, effective_value))
            else:
                setattr(self, attr_name, None)

        counted_entries = list(place_entries)

        counted_codes = [code for code, _ in counted_entries]
        snatch_entries = [entry for entry in counted_entries if entry[0] == Discipline.SNATCH]
        non_snatch_entries = [entry for entry in counted_entries if entry[0] != Discipline.SNATCH]
        total_counted = len(counted_entries)

        if total_counted == 5:
            if len(non_snatch_entries) > 0:
                worst_idx = None
                worst_value = None
                for idx, entry in enumerate(non_snatch_entries):
                    code, place_value = entry
                    if worst_value is None or place_value > worst_value:
                        worst_value = place_value
                        worst_idx = idx
                filtered_non_snatch = [e for i, e in enumerate(non_snatch_entries) if i != worst_idx]
                final_entries = snatch_entries + filtered_non_snatch
            else:
                final_entries = counted_entries
        else:
            final_entries = counted_entries

        if final_entries:
            counted_places = [place for _code, place in final_entries]
            self.counted_disciplines = len(final_entries)
            self.placement_points = float(sum(counted_places))
        else:
            self.counted_disciplines = 0
            self.placement_points = None

        placement_value = self.placement_points
        tiebreak_value = self.tiebreak_points or 0.0
        bonus_value = 0.0

        if placement_value is not None:
            self.total_points = float(placement_value + tiebreak_value + bonus_value)
        elif tiebreak_value or bonus_value:
            self.total_points = float(tiebreak_value + bonus_value)
        else:
            self.total_points = None

        if save:
            self.save(
                update_fields=[
                    "snatch_points",
                    "tgu_points",
                    "squat_points",
                    "see_saw_press_points",
                    "pistol_points",
                    "pull_up_points",
                    "snatch_place",
                    "tgu_place",
                    "squat_place",
                    "see_saw_press_place",
                    "pistol_place",
                    "pull_up_place",
                    "tiebreak_points",
                    "bonus_points",
                    "total_points",
                    "placement_points",
                    "counted_disciplines",
                ]
            )
