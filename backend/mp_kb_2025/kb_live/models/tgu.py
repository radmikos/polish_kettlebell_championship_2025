from django.db import models
from django.utils.translation import gettext_lazy as _
from live_results.services.scoring import tgu_points
from .bases import BaseBWPoints

class TGUResult(BaseBWPoints):
    player = models.OneToOneField(
        "live_results.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="tgu_result",
    )

    class Meta:
        verbose_name = _("Wynik Turkish Get-Up")
        verbose_name_plural = _("Wyniki Turkish Get-Up")

    @property
    def points(self) -> float | None:
        ctx = self._ctx
        if not ctx:
            return None
        return tgu_points(ctx, float(self.kettlebell_weight or 0.0))

    def __str__(self) -> str:
        return f"{self.player} · TGU={self.points if self.points is not None else 'N/A'}"
