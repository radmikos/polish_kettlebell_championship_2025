from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import see_saw_points

from .bases import BaseBWPoints


class SeeSawPressResult(BaseBWPoints):
    """
    Wynik See-Saw Press (2xKB suma) - trzy próby, każda próba to suma wag kettli.
    """

    player = models.OneToOneField(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="see_saw_press_result",
    )
    attempt_1 = models.FloatField(_("Próba 1"), default=0.0, blank=True, null=True)
    attempt_2 = models.FloatField(_("Próba 2"), default=0.0, blank=True, null=True)
    attempt_3 = models.FloatField(_("Próba 3"), default=0.0, blank=True, null=True)

    class Meta:
        verbose_name = _("Wynik See-Saw Press")
        verbose_name_plural = _("Wyniki See-Saw Press")

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
    def points(self) -> float:
        ctx = self._ctx
        if not ctx:
            return 0.0
        val = see_saw_points(ctx, float(self.best_attempt or 0.0))
        return round(val, 3) if val is not None else 0.0

    def __str__(self) -> str:
        return f"{self.player} · See-Saw={self.points if self.points is not None else 'N/A'}"
