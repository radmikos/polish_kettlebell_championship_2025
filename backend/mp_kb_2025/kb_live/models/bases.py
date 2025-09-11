from django.db import models
from django.utils.translation import gettext_lazy as _

from kb_live.services.scoring import Context


class BaseBWPoints(models.Model):
    """
    Baza dla wyników globalnych per zawodnik/konkurencja.
    """

    class Meta:
        abstract = True

    @property
    def _ctx(self) -> Context | None:
        player = getattr(self, "player", None)
        if not player or not player.weight or player.weight <= 0 or player.gender not in {"female", "male"}:
            return None
        return Context(weight=float(player.weight), gender=player.gender)
