from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import snatch_points

from .bases import BaseBWPoints


class SnatchResult(BaseBWPoints):
    player = models.OneToOneField(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="snatch_result",
    )
    kettlebell_weight = models.FloatField(
        _("Waga kettlebell (kg)"),
        default=0.0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
    )
    repetitions = models.IntegerField(
        _("Ilość powtórzeń"),
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = _("Wynik Snatch")
        verbose_name_plural = _("Wyniki Snatch")

    @property
    def points(self) -> float | None:
        ctx = self._ctx
        if not ctx:
            return None
        val = snatch_points(ctx, float(self.kettlebell_weight or 0.0), int(self.repetitions or 0))
        return round(val, 3) if val is not None else None

    def __str__(self) -> str:
        return f"{self.player} · Snatch={self.points if self.points is not None else 'N/A'}"
