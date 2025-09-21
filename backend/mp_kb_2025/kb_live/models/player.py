from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Player(models.Model):
    """Represents a competitor."""

    class Gender(models.TextChoices):
        FEMALE = "Kobieta", _("Kobieta")
        MALE = "Mężczyzna", _("Mężczyzna")

    name = models.CharField(_("Imię"), max_length=50)
    surname = models.CharField(_("Nazwisko"), max_length=50)
    weight = models.FloatField(
        _("Waga (kg)"),
        null=True,
        blank=True,
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )
    gender = models.CharField(
        _("Płeć"),
        max_length=12,
        choices=Gender.choices,
        null=True,
        blank=True,
    )
    @property
    def gender_display(self) -> str:
        return self.get_gender_display() if self.gender else ""

    club = models.ForeignKey(
        "kb_live.SportClub",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Klub"),
        related_name="players",
    )
    categories = models.ManyToManyField(
        "kb_live.Category",
        verbose_name=_("Kategorie"),
        related_name="players",
        blank=True,
    )

    class Meta:
        verbose_name = _("Zawodnik")
        verbose_name_plural = _("Zawodnicy")
        ordering = ["surname", "name"]
        indexes = [
            models.Index(fields=["surname", "name"]),
            models.Index(fields=["gender"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} {self.surname}"

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs) -> None:
        if self.weight is None:
            self.weight = 0.0
        super().save(*args, **kwargs)
