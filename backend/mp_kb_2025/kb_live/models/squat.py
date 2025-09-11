from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import squat_points

from .bases import BaseBWPoints


class SquatResult(BaseBWPoints):
    """
    kettlebell_weight = SUMA dwóch kettli (kg).
    """

    player = models.OneToOneField(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="squat_result",
    )

    class Meta:
        verbose_name = _("Wynik KB Squat (2xKB suma)")
        verbose_name_plural = _("Wyniki KB Squat (2xKB suma)")

    @property
    def points(self) -> float | None:
        ctx = self._ctx
        if not ctx:
            return None
        return squat_points(ctx, float(self.kettlebell_weight or 0.0))

    def __str__(self) -> str:
        return f"{self.player} · Squat={self.points if self.points is not None else 'N/A'}"
