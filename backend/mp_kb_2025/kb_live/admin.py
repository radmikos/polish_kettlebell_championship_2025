from django import forms
from django.contrib import admin
from django.db.models import Q

from .forms import CategoryPlacementForm
from .models import (
    Category,
    CategoryPlacement,
    Discipline,
    PistolResult,
    Player,
    PlayerCategoryTiebreak,
    PullUpResult,
    SeeSawPressResult,
    SnatchResult,
    SportClub,
    SquatResult,
    TGUResult,
)
from .models.overall import CategoryOverallResult


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
    list_display = ("surname", "name", "weight", "gender", "club", "categories_list")
    search_fields = ("surname", "name", "club__name")
    autocomplete_fields = ("club",)
    filter_horizontal = ("categories",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("club").prefetch_related("categories")

    def categories_list(self, obj):
        return ", ".join(obj.categories.values_list("name", flat=True)) or "-"

    categories_list.short_description = "Kategorie"


# --- Tiebreak ---
@admin.register(PlayerCategoryTiebreak)
class PlayerCategoryTiebreakAdmin(admin.ModelAdmin):
    list_display = ("player", "category")
    search_fields = ("player__surname", "player__name", "category__name")
    autocomplete_fields = ("player", "category")
    list_select_related = ("player", "category")


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


# --- NEW: mixin ograniczający wybór zawodnika tylko do kategorii zawierających daną dyscyplinę ---
class _DisciplinePlayerFilterMixin:
    discipline_code: str | None = None  # należy ustawić w podklasie

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if self.discipline_code and "player" in form.base_fields:
            # Gracze posiadający przynajmniej jedną kategorię z tą dyscypliną
            q = Q(categories__disciplines__contains=[self.discipline_code])
            if obj and obj.player_id:
                # zachowaj aktualnego zawodnika nawet jeśli usunięto mu kategorię
                q = Q(pk=obj.player_id) | q
            form.base_fields["player"].queryset = Player.objects.filter(q).distinct().order_by("surname", "name")
        return form


# Snatch admin
@admin.register(SnatchResult)
class SnatchResultAdmin(_DisciplinePlayerFilterMixin, _ResultExtraColumnsMixin, admin.ModelAdmin):
    discipline_code = Discipline.SNATCH
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

    # Override: for snatch show formula points instead of kettlebell weight
    def best_attempt_display(self, obj):
        pts = obj.points
        return round(pts, 3) if pts is not None else "-"

    best_attempt_display.short_description = "Wynik (wzór)"


# Attempts based base admin
class _AttemptsResultAdmin(_DisciplinePlayerFilterMixin, _ResultExtraColumnsMixin, admin.ModelAdmin):
    attempts_fields = ("attempt_1", "attempt_2", "attempt_3")
    search_fields = ("player__surname", "player__name", "player__club__name")
    list_select_related = ("player",)
    readonly_fields = ("points_display", "best_attempt_display", "percent_bw_display", "categories_display")

    def get_list_display(self, request):
        return (
            ("player",)
            + self.attempts_fields
            + ("best_attempt_display", "percent_bw_display", "points_display", "categories_display")
        )


@admin.register(PistolResult)
class PistolResultAdmin(_AttemptsResultAdmin):
    discipline_code = Discipline.PISTOL


@admin.register(SeeSawPressResult)
class SeeSawPressResultAdmin(_AttemptsResultAdmin):
    discipline_code = Discipline.SEE_SAW_PRESS


@admin.register(SquatResult)
class SquatResultAdmin(_AttemptsResultAdmin):
    discipline_code = Discipline.SQUAT


@admin.register(TGUResult)
class TGUResultAdmin(_AttemptsResultAdmin):
    discipline_code = Discipline.TGU


@admin.register(PullUpResult)
class PullUpResultAdmin(_AttemptsResultAdmin):
    discipline_code = Discipline.PULL_UP


# Category placement admin
@admin.register(CategoryPlacement)
class CategoryPlacementAdmin(admin.ModelAdmin):
    form = CategoryPlacementForm
    list_display = ("category", "discipline", "player", "position", "base_points_display", "points_display")
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
    # Kolumny w żądanej kolejności: Zawodnik, Kategorie, punkty z konkurencji, suma, miejsce
    list_display = (
        "player",
        "category_disp",
        "snatch_points_disp",
        "tgu_points_disp",
        "see_saw_press_points_disp",
        "squat_points_disp",
        "pistol_points_disp",
        "pull_up_points_disp",
        "total_points_disp",
        "final_position_disp",
    )
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
    actions = (
        "create_missing_overall",
        "recompute_overall",
        "recompute_overall_and_rank",
    )

    # helper format
    def _fmt(self, value):
        return "-" if value is None else (f"{value:.3f}" if isinstance(value, float) else value)

    def category_disp(self, obj):
        return obj.category

    category_disp.short_description = "Kategorie"
    category_disp.admin_order_field = "category"

    def snatch_points_disp(self, obj):
        return self._fmt(obj.snatch_points)

    snatch_points_disp.short_description = "Punkty Snatch"
    snatch_points_disp.admin_order_field = "snatch_points"

    def tgu_points_disp(self, obj):
        return self._fmt(obj.tgu_points)

    tgu_points_disp.short_description = "Punkty TGU"
    tgu_points_disp.admin_order_field = "tgu_points"

    def see_saw_press_points_disp(self, obj):
        return self._fmt(obj.see_saw_press_points)

    see_saw_press_points_disp.short_description = "Punkty See Saw Press"
    see_saw_press_points_disp.admin_order_field = "see_saw_press_points"

    def squat_points_disp(self, obj):
        return self._fmt(obj.squat_points)

    squat_points_disp.short_description = "Punkty KB Squat"
    squat_points_disp.admin_order_field = "squat_points"

    def pistol_points_disp(self, obj):
        return self._fmt(obj.pistol_points)

    pistol_points_disp.short_description = "Punkty Pistol Squat"
    pistol_points_disp.admin_order_field = "pistol_points"

    def pull_up_points_disp(self, obj):
        return self._fmt(obj.pull_up_points)

    pull_up_points_disp.short_description = "Punkty Pull-Up"
    pull_up_points_disp.admin_order_field = "pull_up_points"

    def total_points_disp(self, obj):
        return self._fmt(obj.total_points)

    total_points_disp.short_description = "Suma punktów"
    total_points_disp.admin_order_field = "total_points"

    def final_position_disp(self, obj):
        # Miejsce = punkty w klasyfikacji generalnej (im mniej tym lepiej)
        return obj.final_position or "-"

    final_position_disp.short_description = "Miejsce końcowe"
    final_position_disp.admin_order_field = "final_position"

    @admin.action(description="Przelicz wyniki ogólne (bez zmiany miejsc)")
    def recompute_overall(self, request, queryset):
        rows = list(queryset.select_related("player", "category"))
        for r in rows:
            r.recompute(save=True)

    @admin.action(description="Przelicz i nadaj miejsca (ASC po sumie miejsc)")
    def recompute_overall_and_rank(self, request, queryset):
        from itertools import groupby

        rows = list(queryset.select_related("player", "category"))
        for r in rows:
            r.recompute(save=True)
        rows.sort(key=lambda r: r.category_id)
        for _, group in groupby(rows, key=lambda r: r.category_id):
            g = list(group)
            g.sort(
                key=lambda r: (
                    r.total_points is None,
                    r.total_points,
                    getattr(r.player, "surname", ""),
                    getattr(r.player, "name", ""),
                )
            )
            for i, r in enumerate(g, start=1):
                r.final_position = i if r.total_points is not None else None
            type(g[0]).objects.bulk_update(g, ["final_position"])

    # Category admin
    @admin.action(description="Utwórz brakujące rekordy Overall i przelicz")
    def create_missing_overall(self, request, queryset):
        from kb_live.models import CategoryOverallResult, Player

        through = Player.categories.through
        pairs = set(through.objects.all().values_list("player_id", "category_id"))
        existing = set(CategoryOverallResult.objects.values_list("player_id", "category_id"))
        missing = pairs - existing
        to_create = [CategoryOverallResult(player_id=p, category_id=c) for p, c in missing]
        if to_create:
            CategoryOverallResult.objects.bulk_create(to_create, ignore_conflicts=True)
            # recompute only new ones
            new_qs = CategoryOverallResult.objects.filter(
                player_id__in=[p for p, _ in missing], category_id__in=[c for _, c in missing]
            ).select_related("player", "category")
            for r in new_qs:
                r.recompute(save=True)
            self.message_user(request, f"Dodano {len(to_create)} nowych rekordów overall.")
        else:
            self.message_user(request, "Brak brakujących rekordów overall.")


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
