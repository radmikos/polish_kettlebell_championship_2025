# live_results/forms.py
from django import forms
from django.core.exceptions import ValidationError
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

    class Meta:
        model = Category
        fields = ["name", "disciplines"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and isinstance(self.instance.disciplines, list):
            self.fields["disciplines"].initial = self.instance.disciplines

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
