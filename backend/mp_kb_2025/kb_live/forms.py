# live_results/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Category, CategoryPlacement, PlayerCategoryParticipation
from .models.choices import Discipline, DISCIPLINE_NAMES

class CategoryForm(forms.ModelForm):
    disciplines = forms.MultipleChoiceField(
        label="Dyscypliny",
        choices=Discipline.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Zaznacz konkurencje dostępne w tej kategorii.",
    )
    drop_worst_result = forms.BooleanField(
        label=_("Odrzucić najgorszy wynik"),
        required=False,
        help_text=_("Jeśli zaznaczysz, najgorszy wynik zawodnika (poza Snatch) nie będzie liczony."),
    )

    class Meta:
        model = Category
        fields = ["name", "disciplines", "drop_worst_result"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and isinstance(self.instance.disciplines, list):
            self.fields["disciplines"].initial = self.instance.disciplines
        if self.instance and self.instance.pk:
            self.fields["drop_worst_result"].initial = bool(self.instance.drop_worst_result)

    def clean_disciplines(self):
        selected = self.cleaned_data.get("disciplines") or []
        valid = {k for k, _ in Discipline.choices}
        invalid = [d for d in selected if d not in valid]
        if invalid:
            raise ValidationError(f"Nieprawidłowe dyscypliny: {', '.join(invalid)}")
        return sorted(selected)


class CategoryPlacementForm(forms.ModelForm):
    class Meta:
        model = CategoryPlacement
        fields = ["category", "discipline", "player", "position"]


class PlayerCategoryParticipationForm(forms.ModelForm):
    class Meta:
        model = PlayerCategoryParticipation
        fields = [
            "category",
            "snatch",
            "tgu",
            "squat",
            "see_saw_press",
            "pistol",
            "pull_up",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pole kategorii tylko do odczytu w inline
        if "category" in self.fields:
            self.fields["category"].disabled = True
        # Ustaw przyjazne etykiety
        labels = {
            "snatch": DISCIPLINE_NAMES.get(Discipline.SNATCH, Discipline.SNATCH),
            "tgu": DISCIPLINE_NAMES.get(Discipline.TGU, Discipline.TGU),
            "squat": DISCIPLINE_NAMES.get(Discipline.SQUAT, Discipline.SQUAT),
            "see_saw_press": DISCIPLINE_NAMES.get(Discipline.SEE_SAW_PRESS, Discipline.SEE_SAW_PRESS),
            "pistol": DISCIPLINE_NAMES.get(Discipline.PISTOL, Discipline.PISTOL),
            "pull_up": DISCIPLINE_NAMES.get(Discipline.PULL_UP, Discipline.PULL_UP),
        }
        for name, label in labels.items():
            if name in self.fields:
                self.fields[name].label = label

        # Pokaż wszystkie pola, ale te spoza kategorii wyłącz (disabled)
        instance = getattr(self, "instance", None)
        allowed = []
        if instance and getattr(instance, "category_id", None):
            allowed = list(instance.category.get_disciplines() or [])
        discipline_fields = [
            (Discipline.SNATCH, "snatch"),
            (Discipline.TGU, "tgu"),
            (Discipline.SQUAT, "squat"),
            (Discipline.SEE_SAW_PRESS, "see_saw_press"),
            (Discipline.PISTOL, "pistol"),
            (Discipline.PULL_UP, "pull_up"),
        ]
        for code, field_name in discipline_fields:
            if field_name in self.fields and code not in allowed:
                field = self.fields[field_name]
                field.required = False
                field.disabled = True
                # Make visually clear it's not part of this category
                field.help_text = (field.help_text or "") + " (Niedostępne w tej kategorii)"
