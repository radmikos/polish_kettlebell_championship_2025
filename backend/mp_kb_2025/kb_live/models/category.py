from django.db import models
from django.utils.translation import gettext_lazy as _

from .choices import DISCIPLINE_NAMES, Discipline


class Category(models.Model):
    """Represents a competition category with specific disciplines."""

    name = models.CharField(_("Nazwa Kategorii"), max_length=100, unique=True)
    disciplines = models.JSONField(_("Dyscypliny"), default=list)
    max_counted_disciplines = models.PositiveSmallIntegerField(
        _("Liczba punktowanych konkurencji"),
        null=True,
        blank=True,
        help_text=_("Ile najlepszych wyników (najniższe miejsca) wliczać do sumy. Pozostaw puste aby liczyć wszystkie."),
    )

    class Meta:
        verbose_name = _("Kategoria")
        verbose_name_plural = _("Kategorie")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def set_disciplines(self, disciplines: list[str]) -> None:
        valid = {d for d, _ in Discipline.choices}
        self.disciplines = sorted([d for d in disciplines if d in valid])

    def get_disciplines(self) -> list[str]:
        return self.disciplines

    def get_disciplines_display(self) -> str:
        return ", ".join(DISCIPLINE_NAMES.get(d, d) for d in self.disciplines)
