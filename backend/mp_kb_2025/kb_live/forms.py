# live_results/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Category, CategoryPlacement
from .models.choices import Discipline

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
