from django.contrib import admin
from django import forms

from .models import (
    SportClub,
    Player,
    Category,
    PlayerCategoryTiebreak,
    SnatchResult,
    PistolResult,
    SeeSawPressResult,
    SquatResult,
    TGUResult,
    PullUpResult,
    CategoryPlacement,
    Discipline,
)
from .models.overall import CategoryOverallResult
from .forms import CategoryPlacementForm

# --- Clubs ---
@admin.register(SportClub)
class SportClubAdmin(admin.ModelAdmin):
    list_display = ("name", "player_count")
    search_fields = ("name",)

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = "Number of Players"

# --- Players ---
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("surname", "name", "gender", "weight", "club")
    list_filter = ("gender", "club", "categories")
    search_fields = ("surname", "name", "club__name")
    autocomplete_fields = ("club",)
    filter_horizontal = ("categories",)

# --- Tiebreak ---
@admin.register(PlayerCategoryTiebreak)
class PlayerCategoryTiebreakAdmin(admin.ModelAdmin):
    list_display = ("player", "category")
    list_filter = ("category",)
    search_fields = ("player__surname", "player__name", "category__name")
    autocomplete_fields = ("player", "category")
    list_select_related = ("player", "category")

# Custom filter for results by player category
class PlayerCategoryFilter(admin.SimpleListFilter):
    title = "Kategorie"
    parameter_name = "player_category"

    def lookups(self, request, model_admin):
        return [(str(c.id), c.name) for c in Category.objects.order_by("name")]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(player__categories__id=self.value()).distinct()
        return queryset

# Shared mixin for extra columns
class _ResultExtraColumnsMixin:
    def categories_display(self, obj):
        return ", ".join(obj.player.categories.values_list("name", flat=True)) or "-"
    categories_display.short_description = "Kategorie"

    def best_attempt_display(self, obj):
        if isinstance(obj, SnatchResult):
            val = obj.kettlebell_weight
        else:
            val = getattr(obj, "best_attempt", None)
        if val is None:
            return "-"
        try:
            return round(float(val), 3)
        except (TypeError, ValueError):
            return "-"
    best_attempt_display.short_description = "Max próba"

    def percent_bw_display(self, obj):
        player = getattr(obj, "player", None)
        if not player or not player.weight or player.weight <= 0:
            return "-"
        if isinstance(obj, SnatchResult):
            base = obj.kettlebell_weight or 0.0
        else:
            base = getattr(obj, "best_attempt", None) or 0.0
        try:
            pct = (float(base) / float(player.weight)) * 100.0
        except (TypeError, ValueError, ZeroDivisionError):
            return "-"
        return f"{pct:.1f}%"
    percent_bw_display.short_description = "% BW"

    def points_display(self, obj):
        return obj.points if obj.points is not None else "N/A"
    points_display.short_description = "Punkty"

# Snatch admin
@admin.register(SnatchResult)
class SnatchResultAdmin(_ResultExtraColumnsMixin, admin.ModelAdmin):
    list_display = (
        "player",
        "repetitions",
        "kettlebell_weight",
        "best_attempt_display",
        "percent_bw_display",
        "points_display",
        "categories_display",
    )
    search_fields = ("player__surname", "player__name", "player__club__name")
    list_select_related = ("player",)
    readonly_fields = ("points_display", "best_attempt_display", "percent_bw_display", "categories_display")
    list_filter = (PlayerCategoryFilter,)

    # Override: for snatch show formula points instead of kettlebell weight
    def best_attempt_display(self, obj):
        pts = obj.points
        return round(pts, 3) if pts is not None else "-"
    best_attempt_display.short_description = "Wynik (wzór)"

# Attempts based base admin
class _AttemptsResultAdmin(_ResultExtraColumnsMixin, admin.ModelAdmin):
    attempts_fields = ("attempt_1", "attempt_2", "attempt_3")
    search_fields = ("player__surname", "player__name", "player__club__name")
    list_select_related = ("player",)
    readonly_fields = ("points_display", "best_attempt_display", "percent_bw_display", "categories_display")
    list_filter = (PlayerCategoryFilter,)

    def get_list_display(self, request):
        return ("player",) + self.attempts_fields + ("best_attempt_display", "percent_bw_display", "points_display", "categories_display")

@admin.register(PistolResult)
class PistolResultAdmin(_AttemptsResultAdmin):
    pass

@admin.register(SeeSawPressResult)
class SeeSawPressResultAdmin(_AttemptsResultAdmin):
    pass

@admin.register(SquatResult)
class SquatResultAdmin(_AttemptsResultAdmin):
    pass

@admin.register(TGUResult)
class TGUResultAdmin(_AttemptsResultAdmin):
    pass

@admin.register(PullUpResult)
class PullUpResultAdmin(_AttemptsResultAdmin):
    pass

# Category placement admin
@admin.register(CategoryPlacement)
class CategoryPlacementAdmin(admin.ModelAdmin):
    form = CategoryPlacementForm
    list_display = ("category", "discipline", "player", "position", "base_points_display", "points_display")
    list_filter = ("category", "discipline")
    search_fields = ("player__surname", "player__name", "category__name")
    autocomplete_fields = ("player", "category")
    list_select_related = ("player", "category")
    ordering = ("category", "discipline", "position", "player__surname")
    actions = ("recompute_positions",)

    def base_points_display(self, obj):
        return obj.base_points
    base_points_display.short_description = "Punkty (bez TB)"

    def points_display(self, obj):
        return obj.points
    points_display.short_description = "Punkty (z TB)"

    @admin.action(description="Nadaj miejsca wg punktów (DESC) dla zaznaczonych wierszy")
    def recompute_positions(self, request, queryset):
        from itertools import groupby
        rows = list(queryset.select_related("player", "category"))
        rows.sort(key=lambda r: (r.category_id, r.discipline))
        for _, group in groupby(rows, key=lambda r: (r.category_id, r.discipline)):
            g = list(group)
            g.sort(key=lambda r: (r.points or -1e18), reverse=True)
            for i, r in enumerate(g, start=1):
                r.position = i if r.points is not None else None
            type(g[0]).objects.bulk_update(g, ["position"])

# Overall category results
@admin.register(CategoryOverallResult)
class CategoryOverallResultAdmin(admin.ModelAdmin):
    list_display = ("category", "player", "total_points", "final_position")
    list_filter = ("category",)
    search_fields = ("player__surname", "player__name", "category__name")
    autocomplete_fields = ("player", "category")
    readonly_fields = (
        "snatch_points",
        "tgu_points",
        "squat_points",
        "see_saw_press_points",
        "pistol_points",
        "pull_up_points",
        "tiebreak_points",
        "total_points",
    )
    actions = ("recompute_overall", "recompute_overall_and_rank",)

    @admin.action(description="Przelicz wyniki ogólne (bez zmiany miejsc)")
    def recompute_overall(self, request, queryset):
        rows = list(queryset.select_related("player", "category"))
        for r in rows:
            r.recompute(save=True)

    @admin.action(description="Przelicz i nadaj miejsca (DESC po total_points)")
    def recompute_overall_and_rank(self, request, queryset):
        from itertools import groupby
        rows = list(queryset.select_related("player", "category"))
        for r in rows:
            r.recompute(save=True)
        rows.sort(key=lambda r: r.category_id)
        for _, group in groupby(rows, key=lambda r: r.category_id):
            g = list(group)
            g.sort(key=lambda r: (r.total_points or -1e18), reverse=True)
            for i, r in enumerate(g, start=1):
                r.final_position = i if r.total_points is not None else None
            type(g[0]).objects.bulk_update(g, ["final_position"])

# Category admin
class CategoryAdminForm(forms.ModelForm):
    disciplines = forms.MultipleChoiceField(
        choices=Discipline.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dyscypliny",
    )
    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["disciplines"].initial = self.instance.disciplines

    def clean_disciplines(self):
        return self.cleaned_data["disciplines"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ("name", "get_disciplines_display")
    search_fields = ("name",)
    ordering = ("name",)

    def get_disciplines_display(self, obj):
        return obj.get_disciplines_display()
    get_disciplines_display.short_description = "Dyscypliny"
