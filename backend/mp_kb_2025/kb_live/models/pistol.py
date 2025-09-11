from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import pistol_points

from .bases import BaseBWPoints


class PistolResult(BaseBWPoints):
    kettlebell_weight = None

    player = models.OneToOneField(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="pistol_result",
    )
    attempt_1 = models.FloatField(_("Próba 1"), default=0.0, blank=True, null=True)
    attempt_2 = models.FloatField(_("Próba 2"), default=0.0, blank=True, null=True)
    attempt_3 = models.FloatField(_("Próba 3"), default=0.0, blank=True, null=True)

    class Meta:
        verbose_name = _("Wynik Pistol Squat")
        verbose_name_plural = _("Wyniki Pistol Squat")

    @property
    def best_attempt(self) -> float:
        return max(
            filter(
                lambda x: x is not None,
                [self.attempt_1, self.attempt_2, self.attempt_3],
            ),
            default=0.0,
        )

    @property
    def points(self) -> float | None:
        ctx = self._ctx
        if not ctx:
            return None
        val = pistol_points(ctx, float(self.best_attempt or 0.0))
        return round(val, 3) if val is not None else None

    def __str__(self) -> str:
        return f"{self.player} · Pistol={self.points if self.points is not None else 'N/A'}"
