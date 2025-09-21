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
    max_counted_disciplines = forms.IntegerField(
        label=_("Liczba punktowanych konkurencji"),
        required=False,
        min_value=1,
        help_text=_("Podaj ile najlepszych wyników ma liczyć się do sumy miejsc. Pozostaw puste aby liczyć wszystkie."),
    )

    class Meta:
        model = Category
        fields = ["name", "disciplines", "max_counted_disciplines"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and isinstance(self.instance.disciplines, list):
            self.fields["disciplines"].initial = self.instance.disciplines
        if self.instance and self.instance.pk:
            self.fields["max_counted_disciplines"].initial = self.instance.max_counted_disciplines

    def clean_disciplines(self):
        selected = self.cleaned_data.get("disciplines") or []
        valid = {k for k, _ in Discipline.choices}
        invalid = [d for d in selected if d not in valid]
        if invalid:
            raise ValidationError(f"Nieprawidłowe dyscypliny: {', '.join(invalid)}")
        return sorted(selected)

    def clean_max_counted_disciplines(self):
        value = self.cleaned_data.get("max_counted_disciplines")
        if value is None:
            return None
        if value <= 0:
            raise ValidationError(_("Wartość musi być dodatnia."))
        return value

    def clean(self):
        cleaned_data = super().clean()
        limit = cleaned_data.get("max_counted_disciplines")
        disciplines = cleaned_data.get("disciplines") or []
        if limit is not None and disciplines and limit > len(disciplines):
            self.add_error(
                "max_counted_disciplines",
                _("Liczba punktowanych konkurencji nie może przekraczać liczby dyscyplin w kategorii."),
            )
        return cleaned_data


class CategoryPlacementForm(forms.ModelForm):
    class Meta:
        model = CategoryPlacement
        fields = ["category", "discipline", "player", "position"]
