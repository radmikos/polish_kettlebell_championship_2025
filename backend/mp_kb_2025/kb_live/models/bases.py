from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from live_results.services.scoring import Context


class BaseBWPoints(models.Model):
    """
    Baza dla wyników globalnych per zawodnik/konkurencja.
    """

    kettlebell_weight = models.FloatField(
        _("Waga kettlebell (kg)"),
        default=0.0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
    )

    class Meta:
        abstract = True

    @property
    def _ctx(self) -> Context | None:
        player = getattr(self, "player", None)
        if not player or not player.weight or player.weight <= 0 or player.gender not in {"female", "male"}:
            return None
        return Context(weight=float(player.weight), gender=player.gender)
