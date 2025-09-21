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
    attempt_1 = models.FloatField(_("Próba 1"), default=0.0, blank=True, null=True)
    attempt_2 = models.FloatField(_("Próba 2"), default=0.0, blank=True, null=True)
    attempt_3 = models.FloatField(_("Próba 3"), default=0.0, blank=True, null=True)

    class Meta:
        verbose_name = _("Wynik Pull-Up")
        verbose_name_plural = _("Wyniki Pull-Up")

    @property
    def best_attempt(self) -> float:
        return max(
            filter(lambda x: x is not None, [self.attempt_1, self.attempt_2, self.attempt_3]),
            default=0.0,
        )

    @property
    def points(self) -> float:
        ctx = self._ctx
        if not ctx:
            return 0.0
        val = pull_up_points(ctx, float(self.best_attempt or 0.0))
        return round(val, 3) if val is not None else 0.0

    def __str__(self) -> str:
        return f"{self.player} · Pull-Up={self.points if self.points is not None else 'N/A'}"
