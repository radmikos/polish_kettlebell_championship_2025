from django.contrib import admin
from .models import (
    SportClub, Player, Category, PlayerCategoryTiebreak,
    SnatchResult, PistolResult, SeeSawPressResult, SquatResult, TGUResult, PullUpResult,
    CategoryPlacement,Discipline,
)
from .models.overall import CategoryOverallResult
from django import forms
# --- Proste modele ---

@admin.register(SportClub)
class SportClubAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("surname", "name", "gender", "weight", "club")
    list_filter = ("gender", "club")
    search_fields = ("surname", "name", "club__name")
    autocomplete_fields = ("club",)
    filter_horizontal = ("categories",)


from django.contrib import admin
from .models import Category



@admin.register(PlayerCategoryTiebreak)
class PlayerCategoryTiebreakAdmin(admin.ModelAdmin):
    list_display = ("player", "category")
    list_filter = ("category",)
    search_fields = ("player__surname", "player__name", "category__name")
    autocomplete_fields = ("player", "category")
    list_select_related = ("player", "category")


# --- Wyniki globalne ---

@admin.register(SnatchResult, PistolResult, SeeSawPressResult, SquatResult, TGUResult, PullUpResult)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("player", "points_display")
    search_fields = ("player__surname", "player__name", "player__club__name")
    list_select_related = ("player",)
    readonly_fields = ("points_preview",)

    def points_display(self, obj):
        return obj.points
    points_display.short_description = "Punkty"

    def points_preview(self, obj):
        return obj.points
    points_preview.short_description = "Punkty (read-only)"


# --- Miejsca per kategoria + akcja do nadawania miejsc ---

from .forms import CategoryPlacementForm  # patrz plik forms.py poniżej

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



class CategoryOverallInline(admin.TabularInline):
    model = CategoryOverallResult
    extra = 0
    fields = ("player", "total_points", "final_position",
              "snatch_points", "tgu_points", "squat_points", "see_saw_press_points", "pistol_points", "pull_up_points",
              "tiebreak_points")
    readonly_fields = ("snatch_points", "tgu_points", "squat_points", "see_saw_press_points",
                       "pistol_points", "pull_up_points", "tiebreak_points", "total_points")
    autocomplete_fields = ("player",)
    ordering = ("final_position", "-total_points")

@admin.register(CategoryOverallResult)
class CategoryOverallResultAdmin(admin.ModelAdmin):
    list_display = ("category", "player", "total_points", "final_position")
    list_filter = ("category",)
    search_fields = ("player__surname", "player__name", "category__name")
    autocomplete_fields = ("player", "category")
    readonly_fields = ("snatch_points", "tgu_points", "squat_points", "see_saw_press_points",
                       "pistol_points", "pull_up_points", "tiebreak_points", "total_points")
    actions = ("recompute_overall", "recompute_overall_and_rank",)

    @admin.action(description="Przelicz wyniki ogólne (bez zmiany miejsc)")
    def recompute_overall(self, request, queryset):
        rows = list(queryset.select_related("player", "category"))
        for r in rows:
            r.recompute(save=True)

    @admin.action(description="Przelicz i nadaj miejsca (DESC po total_points)")
    def recompute_overall_and_rank(self, request, queryset):
        # grupuj per kategoria
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

from django.contrib import admin
from .models import Category, CategoryPlacement, CategoryOverallResult, Discipline
from .forms import CategoryForm, CategoryPlacementForm

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm   # <- TO jest wymagane; nie ustawiaj None
    list_display = ("name", "get_disciplines_display")
    search_fields = ("name",)
    # jeśli używasz inline z overall:
    # inlines = [CategoryOverallInline]
