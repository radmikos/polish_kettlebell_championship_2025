from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import tgu_points

from .bases import BaseBWPoints


class TGUResult(BaseBWPoints):
    player = models.OneToOneField(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="tgu_result",
    )
    attempt_1 = models.FloatField(_("Próba 1"), default=0.0, blank=True, null=True)
    attempt_2 = models.FloatField(_("Próba 2"), default=0.0, blank=True, null=True)
    attempt_3 = models.FloatField(_("Próba 3"), default=0.0, blank=True, null=True)
    place = models.PositiveIntegerField(_("Miejsce"), null=True, blank=True)

    class Meta:
        verbose_name = _("Wynik Turkish Get-Up")
        verbose_name_plural = _("Wyniki Turkish Get-Up")

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
        val = tgu_points(ctx, float(self.best_attempt or 0.0))
        if val is None:
            return None
        return round(val, 3)

    def __str__(self) -> str:
        return f"{self.player} · TGU={self.points if self.points is not None else 'N/A'}"
