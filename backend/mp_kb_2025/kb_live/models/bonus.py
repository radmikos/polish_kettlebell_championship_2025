
from __future__ import annotations

from typing import Any, Tuple

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .choices import Discipline

BONUS_CACHE_ATTR = "_discipline_bonus_cache"


def _safe_points(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _build_category_bonus_cache(category: Any) -> dict[int, dict[str, Any]]:
    cache: dict[int, dict[str, Any]] = {}
    entries = category.bonus_points_assigned.all() if category else []
    for entry in entries:
        points = _safe_points(entry.points)
        if not points:
            continue
        player_cache = cache.setdefault(entry.player_id, {"general": 0.0, "disciplines": {}})
        if entry.discipline:
            disciplines: dict[str, float] = player_cache.setdefault("disciplines", {})
            disciplines[entry.discipline] = disciplines.get(entry.discipline, 0.0) + points
        else:
            player_cache["general"] = _safe_points(player_cache.get("general")) + points
    return cache


def get_category_bonus_cache(category: Any) -> dict[int, dict[str, Any]]:
    if category is None:
        return {}
    cache = getattr(category, BONUS_CACHE_ATTR, None)
    if cache is None:
        cache = _build_category_bonus_cache(category)
        setattr(category, BONUS_CACHE_ATTR, cache)
    return cache


def get_player_bonus_share(category: Any, player_id: int) -> Tuple[float, dict[str, float]]:
    cache = get_category_bonus_cache(category)
    data = cache.get(player_id)
    if not data:
        return 0.0, {}
    general = _safe_points(data.get("general"))
    disciplines = {
        code: _safe_points(value)
        for code, value in (data.get("disciplines") or {}).items()
    }
    return general, disciplines


def clear_category_bonus_cache(category: Any | None) -> None:
    if category is not None and hasattr(category, BONUS_CACHE_ATTR):
        delattr(category, BONUS_CACHE_ATTR)


class PlayerCategoryBonus(models.Model):
    """Custom bonus points assigned to a player within a category and discipline."""

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
    discipline = models.CharField(
        _("Dyscyplina"),
        max_length=32,
        choices=Discipline.choices,
        blank=True,
        null=True,
        help_text=_("Konkurencja, której dotyczą dodatkowe punkty."),
    )
    points = models.FloatField(
        _("Dodatkowe punkty"),
        default=0.0,
        help_text=_("Liczba punktów dodanych do wskazanej konkurencji w ramach kategorii."),
    )

    class Meta:
        verbose_name = _("Dodatkowe punkty (Zawodnik-Kategoria-Dyscyplina)")
        verbose_name_plural = _("Dodatkowe punkty (Zawodnik-Kategoria-Dyscyplina)")
        ordering = ["player__surname", "player__name", "category__name", "discipline"]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "category", "discipline"],
                name="uniq_player_category_discipline_bonus",
            ),
        ]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["player"]),
            models.Index(fields=["discipline"]),
        ]

    def __str__(self) -> str:
        discipline_label = self.get_discipline_display()
        return f"Bonus: {self.player} · {self.category} · {discipline_label} (+{self.points:g})"

    def clean(self) -> None:
        super().clean()
        category = getattr(self, "category", None)
        if category:
            if not self.discipline:
                raise ValidationError({"discipline": _("Wybierz dyscyplinę powiązaną z tą kategorią.")})
            allowed = set(category.get_disciplines() or [])
            if allowed and self.discipline not in allowed:
                raise ValidationError({"discipline": _("Wybrana dyscyplina nie jest dostępna w tej kategorii.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        result = super().save(*args, **kwargs)
        clear_category_bonus_cache(getattr(self, "category", None))
        return result

    def delete(self, *args, **kwargs):
        category = getattr(self, "category", None)
        result = super().delete(*args, **kwargs)
        clear_category_bonus_cache(category)
        return result

