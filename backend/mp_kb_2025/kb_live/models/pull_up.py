from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import pull_up_points

from .bases import BaseBWPoints


class PullUpResult(BaseBWPoints):
    """
    pull-up: finalWeight = body_weight + dodatkowy ciężar (kettlebell_weight)
    """

    player = models.OneToOneField(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="pull_up_result",
    )

    class Meta:
        verbose_name = _("Wynik Pull-Up")
        verbose_name_plural = _("Wyniki Pull-Up")

    @property
    def points(self) -> float | None:
        ctx = self._ctx
        if not ctx:
            return None
        return pull_up_points(ctx, float(self.kettlebell_weight or 0.0))

    def __str__(self) -> str:
        return f"{self.player} · Pull-Up={self.points if self.points is not None else 'N/A'}"
