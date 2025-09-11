from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import see_saw_points

from .bases import BaseBWPoints


class SeeSawPressResult(BaseBWPoints):
    """
    kettlebell_weight = SUMA dwóch kettli (kg).
    """

    player = models.OneToOneField(
        "kb_live.Player",
        on_delete=models.CASCADE,
        verbose_name=_("Zawodnik"),
        related_name="see_saw_press_result",
    )

    class Meta:
        verbose_name = _("Wynik See-Saw Press")
        verbose_name_plural = _("Wyniki See-Saw Press")

    @property
    def points(self) -> float | None:
        ctx = self._ctx
        if not ctx:
            return None
        return see_saw_points(ctx, float(self.kettlebell_weight or 0.0))

    def __str__(self) -> str:
        return f"{self.player} · See-Saw={self.points if self.points is not None else 'N/A'}"
