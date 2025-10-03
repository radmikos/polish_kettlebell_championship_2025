from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F, FloatField, ExpressionWrapper, Case, When, Value
from django.db.models.functions import Greatest

from .forms import CategoryPlacementForm
from .models import (
    Category,
    CategoryPlacement,
    Discipline,
    PistolResult,
    Player,
    PlayerCategoryBonus,
    PlayerCategoryTiebreak,
    PullUpResult,
    SeeSawPressResult,
    SnatchResult,
    SportClub,
    SquatResult,
    TGUResult,
)
from import_export.admin import ImportExportModelAdmin
from .resources import PlayerImportResource, PlayerExportResource
from .models.overall import CategoryOverallResult
from .services.ranking import rank_category_overall
from .models.choices import DISCIPLINE_NAMES


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
class PlayerAdmin(ImportExportModelAdmin):
    resource_classes = [PlayerImportResource]
    export_resource_classes = [PlayerExportResource]
    list_display = ("surname", "name", "weight", "gender", "club", "categories_list")
    search_fields = ("surname", "name", "club__name", "categories__name")
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


@admin.register(PlayerCategoryBonus)
class PlayerCategoryBonusAdmin(admin.ModelAdmin):
    list_display = ("player", "category", "points")
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
    # allow ordering by annotated best_attempt_value when available
    best_attempt_display.admin_order_field = "best_attempt_value"

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
        "place",
        "best_attempt_display",
        "percent_bw_display",
        "points_display",
        "categories_display",
    )
    search_fields = ("player__surname", "player__name", "player__club__name")
    list_select_related = ("player",)
    readonly_fields = (
        "place",
        "points_display",
        "best_attempt_display",
        "percent_bw_display",
        "categories_display",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # annotate with kettlebell_weight as best_attempt_value and percent BW
        percent_ratio = ExpressionWrapper(
            F("kettlebell_weight") * 1.0 / F("player__weight"), output_field=FloatField()
        )
        qs = qs.select_related("player").annotate(
            best_attempt_value=F("kettlebell_weight"),
            percent_bw_value=Case(
                When(player__weight__gt=0, then=percent_ratio),
                default=Value(None),
                output_field=FloatField(),
            ),
        )
        return qs

    # Override: for snatch show formula points instead of kettlebell weight
    def best_attempt_display(self, obj):
        pts = obj.points
        return round(pts, 3) if pts is not None else "-"

    best_attempt_display.short_description = "Wynik (wzór)"
    # ordering for snatch: order by annotated best attempt value (kettlebell_weight)
    # admin_order_field assignments for the overridden methods are set below


# Attempts based base admin
class _AttemptsResultAdmin(_DisciplinePlayerFilterMixin, _ResultExtraColumnsMixin, admin.ModelAdmin):
    attempts_fields = ("attempt_1", "attempt_2", "attempt_3")
    search_fields = ("player__surname", "player__name", "player__club__name")
    list_select_related = ("player",)
    readonly_fields = (
        "place",
        "points_display",
        "best_attempt_display",
        "percent_bw_display",
        "categories_display",
    )

    def get_list_display(self, request):
        return (
            ("player",)
            + self.attempts_fields
            + (
                "place",
                "best_attempt_display",
                "percent_bw_display",
                "points_display",
                "categories_display",
            )
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # annotate greatest of attempts as best_attempt_value and percent of BW
        best_attempt_expr = Greatest(*self.attempts_fields)
        percent_ratio = ExpressionWrapper(
            best_attempt_expr * 1.0 / F("player__weight"), output_field=FloatField()
        )
        qs = qs.select_related("player").annotate(
            best_attempt_value=best_attempt_expr,
            percent_bw_value=Case(
                When(player__weight__gt=0, then=percent_ratio),
                default=Value(None),
                output_field=FloatField(),
            ),
        )
        return qs


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


# Overall category results
@admin.register(CategoryOverallResult)
class CategoryOverallResultAdmin(admin.ModelAdmin):
    CATEGORY_FILTER_PARAM = "category__id__exact"
    DISCIPLINE_POINTS_FIELDS = {
        Discipline.SNATCH: "snatch_points",
        Discipline.TGU: "tgu_points",
        Discipline.SQUAT: "squat_points",
        Discipline.SEE_SAW_PRESS: "see_saw_press_points",
        Discipline.PISTOL: "pistol_points",
        Discipline.PULL_UP: "pull_up_points",
    }
    ORDERED_DISCIPLINE_CODES = [
        Discipline.SNATCH,
        Discipline.TGU,
        Discipline.SEE_SAW_PRESS,
        Discipline.SQUAT,
        Discipline.PISTOL,
        Discipline.PULL_UP,
    ]
    change_list_template = "admin/kb_live/categoryoverallresult/change_list.html"
    # Kolumny w żądanej kolejności: Zawodnik, Kategorie, punkty z konkurencji, suma, miejsce
    list_display = (
        "player_link",
        "get_player_categories_display",
        "category_disp",
        "snatch_place_disp",
        "snatch_points_disp",
        "tgu_place_disp",
        "tgu_points_disp",
        "see_saw_press_place_disp",
        "see_saw_press_points_disp",
        "squat_place_disp",
        "squat_points_disp",
        "pistol_place_disp",
        "pistol_points_disp",
        "pull_up_place_disp",
        "pull_up_points_disp",
        "bonus_points_disp",
        "placement_points_disp",
        "total_points_disp",
        "final_position_disp",
    )
    list_display_links = ("category_disp",)
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
        "snatch_place",
        "tgu_place",
        "squat_place",
        "see_saw_press_place",
        "pistol_place",
        "pull_up_place",
        "tiebreak_points",
        "bonus_points",
        "total_points",
        "placement_points",
        "counted_disciplines",
    )
    actions = (
        "export_overall_results_as_html",
        "create_missing_overall",
        "recompute_overall",
        "recompute_overall_and_rank",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("player", "player__club", "category").prefetch_related("player__categories")
        category_filter_value = request.GET.get(self.CATEGORY_FILTER_PARAM)
        if category_filter_value:
            qs = qs.filter(category_id=category_filter_value)
        return qs

    def changelist_view(self, request, extra_context=None):
        category_choices = Category.objects.order_by("name")
        selected_category = request.GET.get(self.CATEGORY_FILTER_PARAM, "")

        extra_context = extra_context or {}
        extra_context.update(
            {
                "category_filter_choices": category_choices,
                "selected_category_filter": selected_category,
                "category_filter_param_name": self.CATEGORY_FILTER_PARAM,
            }
        )
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description=_("Zawodnik"), ordering="player__surname")
    def player_link(self, obj: CategoryOverallResult):
        player = getattr(obj, "player", None)
        if not player:
            return "-"
        url = reverse("admin:kb_live_player_change", args=[player.pk])
        return format_html('<a href="{}">{}</a>', url, player.full_name)

    @admin.display(description=_("Kategorie"))
    def get_player_categories_display(self, obj: CategoryOverallResult) -> str:
        player = getattr(obj, "player", None)
        if not player:
            return "-"
        categories = getattr(player, "_prefetched_objects_cache", {}).get("categories")
        if categories is None:
            categories = list(player.categories.all())
        names = [c.name for c in categories]
        return ", ".join(names) if names else "-"

    # helper format
    def _fmt(self, value):
        return "-" if value is None else (f"{value:.3f}" if isinstance(value, float) else value)

    def category_disp(self, obj):
        return obj.category

    category_disp.short_description = _("Kategoria")
    category_disp.admin_order_field = "category"

    def snatch_points_disp(self, obj):
        return self._fmt(obj.snatch_points)

    snatch_points_disp.short_description = "Punkty Snatch"
    snatch_points_disp.admin_order_field = "snatch_points"

    def tgu_points_disp(self, obj):
        return self._fmt(obj.tgu_points)

    tgu_points_disp.short_description = "Punkty TGU"
    tgu_points_disp.admin_order_field = "tgu_points"

    def snatch_place_disp(self, obj):
        return obj.snatch_place or "-"

    snatch_place_disp.short_description = "Miejsce Snatch"
    snatch_place_disp.admin_order_field = "snatch_place"

    def tgu_place_disp(self, obj):
        return obj.tgu_place or "-"

    tgu_place_disp.short_description = "Miejsce TGU"
    tgu_place_disp.admin_order_field = "tgu_place"

    def see_saw_press_points_disp(self, obj):
        return self._fmt(obj.see_saw_press_points)

    see_saw_press_points_disp.short_description = "Punkty See Saw Press"
    see_saw_press_points_disp.admin_order_field = "see_saw_press_points"

    def see_saw_press_place_disp(self, obj):
        return obj.see_saw_press_place or "-"

    see_saw_press_place_disp.short_description = "Miejsce See Saw Press"
    see_saw_press_place_disp.admin_order_field = "see_saw_press_place"

    def squat_points_disp(self, obj):
        return self._fmt(obj.squat_points)

    squat_points_disp.short_description = "Punkty KB Squat"
    squat_points_disp.admin_order_field = "squat_points"

    def squat_place_disp(self, obj):
        return obj.squat_place or "-"

    squat_place_disp.short_description = "Miejsce KB Squat"
    squat_place_disp.admin_order_field = "squat_place"

    def pistol_points_disp(self, obj):
        return self._fmt(obj.pistol_points)

    pistol_points_disp.short_description = "Punkty Pistol Squat"
    pistol_points_disp.admin_order_field = "pistol_points"

    def pistol_place_disp(self, obj):
        return obj.pistol_place or "-"

    pistol_place_disp.short_description = "Miejsce Pistol Squat"
    pistol_place_disp.admin_order_field = "pistol_place"

    def pull_up_points_disp(self, obj):
        return self._fmt(obj.pull_up_points)

    pull_up_points_disp.short_description = "Punkty Pull-Up"
    pull_up_points_disp.admin_order_field = "pull_up_points"

    def pull_up_place_disp(self, obj):
        return obj.pull_up_place or "-"

    pull_up_place_disp.short_description = "Miejsce Pull-Up"
    pull_up_place_disp.admin_order_field = "pull_up_place"

    def bonus_points_disp(self, obj):
        return self._fmt(obj.bonus_points)

    bonus_points_disp.short_description = "Punkty dodatkowe"
    bonus_points_disp.admin_order_field = "bonus_points"

    def placement_points_disp(self, obj):
        return self._fmt(obj.placement_points)

    placement_points_disp.short_description = "Suma punktów z miejsc"
    placement_points_disp.admin_order_field = "placement_points"

    def total_points_disp(self, obj):
        return self._fmt(obj.total_points)

    total_points_disp.short_description = "Suma punktów (konkurencje)"
    total_points_disp.admin_order_field = "total_points"

    def final_position_disp(self, obj):
        # Miejsce wg sumy punktów z miejsc (niższa wartość jest lepsza)
        return obj.final_position if obj.final_position is not None else "-"

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
        if not rows:
            return
        category_ids = set()
        for r in rows:
            r.recompute(save=True)
            category_ids.add(r.category_id)
        for cat_id in category_ids:
            rank_category_overall(cat_id)

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

    @admin.action(description=_("Eksportuj podsumowanie wyników do HTML"))
    def export_overall_results_as_html(self, request, queryset):
        results_qs = (
            queryset.select_related("player", "player__club", "category")
            .prefetch_related("player__categories")
            .order_by(
                "category__name",
                "final_position",
                "placement_points",
                "-total_points",
                "player__surname",
                "player__name",
            )
        )

        if not results_qs.exists():
            self.message_user(request, _("Brak wyników do wyeksportowania."))
            return

        results = list(results_qs)

        discipline_candidates: set[str] = set()
        for result in results:
            category_disciplines = getattr(result.category, "disciplines", None) or []
            discipline_candidates.update(code for code in category_disciplines if isinstance(code, str))

        if not discipline_candidates:
            discipline_candidates = set(self.ORDERED_DISCIPLINE_CODES)

        discipline_columns = [
            {
                "code": code,
                "name": DISCIPLINE_NAMES.get(code, code),
                "field_name": self.DISCIPLINE_POINTS_FIELDS[code],
            }
            for code in self.ORDERED_DISCIPLINE_CODES
            if code in discipline_candidates and code in self.DISCIPLINE_POINTS_FIELDS
        ]

        rows = []
        for result in results:
            categories = getattr(result.player, "_prefetched_objects_cache", {}).get("categories")
            if categories is None:
                categories = list(result.player.categories.all())
            categories_str = ", ".join(cat.name for cat in categories) if categories else "---"
            rows.append({"result": result, "categories_str": categories_str})

        title = _("Podsumowanie Wyników Ogólnych")
        category_names = sorted({r.category.name for r in results if getattr(r, "category", None)})
        if len(category_names) == 1:
            title = f"{title} — {category_names[0]}"

        context = {
            "title": title,
            "results_with_cats": rows,
            "discipline_columns": discipline_columns,
        }

        html_content = render_to_string("kb_live/export_results.html", context)
        response = HttpResponse(html_content, content_type="text/html; charset=utf-8")

        filename = "overall_results.html"
        if len(category_names) == 1 and category_names[0]:
            filename = f"overall_results_{slugify(category_names[0])}.html"

        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


# -- Set admin_order_field attributes for mixin display methods that rely on annotated fields
# For attempt-based admins, order by annotated best_attempt_value / percent_bw_value
_AttemptsResultAdmin.best_attempt_display.admin_order_field = "best_attempt_value"
_AttemptsResultAdmin.percent_bw_display.admin_order_field = "percent_bw_value"
_AttemptsResultAdmin.points_display.admin_order_field = "best_attempt_value"

# For snatch admin (kettlebell_weight used as best_attempt_value)
SnatchResultAdmin.best_attempt_display.admin_order_field = "best_attempt_value"
SnatchResultAdmin.percent_bw_display.admin_order_field = "percent_bw_value"
SnatchResultAdmin.points_display.admin_order_field = "best_attempt_value"


class CategoryAdminForm(forms.ModelForm):
    disciplines = forms.MultipleChoiceField(
        choices=Discipline.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dyscypliny",
    )
    drop_worst_result = forms.BooleanField(
        required=False,
        label="Odrzuć najgorszy wynik",
        help_text="Jeśli zaznaczone, najgorszy wynik zawodnika (poza Snatch) nie będzie liczony w klasyfikacji.",
    )

    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["disciplines"].initial = self.instance.disciplines
            self.fields["drop_worst_result"].initial = bool(self.instance.drop_worst_result)

    def clean_disciplines(self):
        return sorted(self.cleaned_data["disciplines"])


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ("name", "get_disciplines_display", "drop_worst_result_display")
    search_fields = ("name",)
    ordering = ("name",)

    def get_disciplines_display(self, obj):
        return obj.get_disciplines_display()

    get_disciplines_display.short_description = "Dyscypliny"

    def drop_worst_result_display(self, obj):
        return "Tak" if obj.drop_worst_result else "Nie"

    drop_worst_result_display.short_description = "Odrzuć najgorszy wynik"
