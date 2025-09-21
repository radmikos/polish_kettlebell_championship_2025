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
        if not player or not player.weight or player.weight <= 0:
            return None

        gender_raw = (player.gender or "").strip()
        if not gender_raw:
            return None

        gender_map = {
            "kobieta": "female",
            "mężczyzna": "male",
            "mezczyzna": "male",
            "female": "female",
            "male": "male",
        }

        gender_norm = gender_map.get(gender_raw.lower())
        if gender_norm is None:
            return None

        return Context(weight=float(player.weight), gender=gender_norm)
