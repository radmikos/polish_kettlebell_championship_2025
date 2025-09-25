"""REST API endpoints for live results in the Polish KB Championship project."""

from __future__ import annotations

from collections import defaultdict

from django.db.models import Prefetch, Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from kb_live.models import Category, CategoryOverallResult, CategoryPlacement, Discipline, Player, SportClub
from kb_live.serializers import (
    CategoryListSerializer,
    CategoryPlacementSerializer,
    CategoryResultsSerializer,
    PlayerDetailSerializer,
    PlayerSummarySerializer,
    SportClubSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.order_by("name")
    serializer_class = CategoryListSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def disciplines(self, request):
        """Return available discipline codes and their human-friendly labels."""
        data = [
            {"code": code, "label": label}
            for code, label in Discipline.choices
        ]
        return Response(data)

    @action(detail=True, methods=["get"], serializer_class=CategoryResultsSerializer)
    def results(self, request, pk=None):
        """Provide full standings for a single category."""
        category = self.get_object()
        overall_qs = (
            CategoryOverallResult.objects.filter(category=category)
            .select_related("player", "player__club")
            .prefetch_related(
                "player__categories",
                "player__snatch_result",
                "player__tgu_result",
                "player__squat_result",
                "player__see_saw_press_result",
                "player__pistol_result",
                "player__pull_up_result",
            )
            .order_by("final_position", "total_points", "player__surname", "player__name")
        )

        placements_qs = (
            CategoryPlacement.objects.filter(category=category)
            .select_related("player", "player__club")
            .prefetch_related("player__categories")
        )

        placements_map: dict[int, dict[str, CategoryPlacement]] = defaultdict(dict)
        for placement in placements_qs:
            placements_map[placement.player_id][placement.discipline] = placement

        context = self.get_serializer_context()
        context.update({
            "category": category,
            "placements_map": placements_map,
        })

        serializer = self.get_serializer(overall_qs, many=True, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], serializer_class=CategoryPlacementSerializer)
    def placements(self, request, pk=None):
        """List placements per discipline for a category."""
        category = self.get_object()
        queryset = (
            CategoryPlacement.objects.filter(category=category)
            .select_related("player", "player__club")
            .prefetch_related("player__categories")
            .order_by("discipline", "position", "player__surname", "player__name")
        )
        tiebreak_players = set(category.tiebreaks_applied.values_list("player_id", flat=True))
        context = self.get_serializer_context()
        context.update({"tiebreak_players": tiebreak_players})
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        base_qs = Player.objects.select_related("club")

        if getattr(self, "action", None) == "retrieve":
            base_qs = base_qs.select_related(
                "snatch_result",
                "tgu_result",
                "squat_result",
                "see_saw_press_result",
                "pistol_result",
                "pull_up_result",
            ).prefetch_related(
                "categories",
                Prefetch(
                    "category_results",
                    queryset=CategoryOverallResult.objects.select_related("category").order_by("category__name"),
                ),
            )
        else:
            base_qs = base_qs.prefetch_related("categories")

        category_id = self.request.query_params.get("category") if self.request else None
        if category_id:
            base_qs = base_qs.filter(categories__id=category_id)

        gender = self.request.query_params.get("gender") if self.request else None
        if gender:
            base_qs = base_qs.filter(gender=gender)

        search = self.request.query_params.get("search") if self.request else None
        if search:
            base_qs = base_qs.filter(Q(name__icontains=search) | Q(surname__icontains=search))

        return base_qs.order_by("surname", "name").distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PlayerDetailSerializer
        return PlayerSummarySerializer


class SportClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SportClub.objects.order_by("name")
    serializer_class = SportClubSerializer
    permission_classes = [permissions.AllowAny]
