from django.db.models import TextChoices


class Discipline(TextChoices):
    SNATCH = "snatch", "Snatch"
    TGU = "tgu", "Turkish Get-Up"
    SQUAT = "squat", "Kettlebell Squat (2xKB)"
    SEE_SAW_PRESS = "see_saw_press", "See-Saw Press (2xKB)"
    PISTOL = "pistol", "Pistol Squat"
    PULL_UP = "pull_up", "Pull-Up"


DISCIPLINE_NAMES = dict(Discipline.choices)
