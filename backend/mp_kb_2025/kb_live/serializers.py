"""Serializers exposing live results for the Polish KB Championship API."""

from __future__ import annotations

from collections.abc import Mapping

from rest_framework import serializers

from kb_live.models import (
    DISCIPLINE_NAMES,
    Category,
    CategoryOverallResult,
    CategoryPlacement,
    Player,
    SportClub,
)


def _serialize_disciplines(category: Category) -> list[dict[str, str]]:
    codes = category.get_disciplines() if hasattr(category, "get_disciplines") else []
    return [
        {"code": code, "label": DISCIPLINE_NAMES.get(code, code)}
        for code in codes
    ]


class SportClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportClub
        fields = ("id", "name")
        read_only_fields = fields


class CategoryBaseSerializer(serializers.ModelSerializer):
    disciplines = serializers.ListField(read_only=True)
    disciplines_verbose = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "disciplines", "disciplines_verbose", "drop_worst_result")
        read_only_fields = fields

    def get_disciplines_verbose(self, obj: Category) -> list[dict[str, str]]:
        return _serialize_disciplines(obj)


class CategoryListSerializer(CategoryBaseSerializer):
    pass


class CategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = fields


class PlayerSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    gender_display = serializers.CharField(read_only=True)
    club = SportClubSerializer(read_only=True)
    categories = CategoryNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = (
            "id",
            "name",
            "surname",
            "full_name",
            "gender",
            "gender_display",
            "weight",
            "club",
            "categories",
        )
        read_only_fields = fields


class PlayerDetailSerializer(PlayerSummarySerializer):
    snatch_result = serializers.SerializerMethodField()
    tgu_result = serializers.SerializerMethodField()
    squat_result = serializers.SerializerMethodField()
    see_saw_press_result = serializers.SerializerMethodField()
    pistol_result = serializers.SerializerMethodField()
    pull_up_result = serializers.SerializerMethodField()
    overall_results = serializers.SerializerMethodField()

    class Meta(PlayerSummarySerializer.Meta):
        fields = PlayerSummarySerializer.Meta.fields + (
            "snatch_result",
            "tgu_result",
            "squat_result",
            "see_saw_press_result",
            "pistol_result",
            "pull_up_result",
            "overall_results",
        )

    def _serialize_attempts(self, result) -> dict[str, float | None] | None:
        if result is None:
            return None
        data = {
            "attempt_1": result.attempt_1,
            "attempt_2": result.attempt_2,
            "attempt_3": result.attempt_3,
            "best_attempt": getattr(result, "best_attempt", None),
            "points": getattr(result, "points", None),
            "place": getattr(result, "place", None),
        }
        return data

    def _serialize_snatch(self, result) -> dict[str, float | None] | None:
        if result is None:
            return None
        return {
            "kettlebell_weight": result.kettlebell_weight,
            "repetitions": result.repetitions,
            "points": getattr(result, "points", None),
            "place": getattr(result, "place", None),
        }

    def get_snatch_result(self, obj: Player):
        return self._serialize_snatch(getattr(obj, "snatch_result", None))

    def get_tgu_result(self, obj: Player):
        return self._serialize_attempts(getattr(obj, "tgu_result", None))

    def get_squat_result(self, obj: Player):
        return self._serialize_attempts(getattr(obj, "squat_result", None))

    def get_see_saw_press_result(self, obj: Player):
        return self._serialize_attempts(getattr(obj, "see_saw_press_result", None))

    def get_pistol_result(self, obj: Player):
        return self._serialize_attempts(getattr(obj, "pistol_result", None))

    def get_pull_up_result(self, obj: Player):
        return self._serialize_attempts(getattr(obj, "pull_up_result", None))

    def get_overall_results(self, obj: Player) -> list[dict[str, object]]:
        rows_manager = getattr(obj, "category_results", None)
        rows = rows_manager.all() if hasattr(rows_manager, "all") else (rows_manager or [])
        output: list[dict[str, object]] = []
        for row in rows:
            output.append(
                {
                    "category": CategoryNestedSerializer(row.category).data,
                    "final_position": row.final_position,
                    "total_points": row.total_points,
                    "discipline_places": {
                        "snatch": row.snatch_place,
                        "tgu": row.tgu_place,
                        "squat": row.squat_place,
                        "see_saw_press": row.see_saw_press_place,
                        "pistol": row.pistol_place,
                        "pull_up": row.pull_up_place,
                    },
                    "placement_points": row.placement_points,
                    "counted_disciplines": row.counted_disciplines,
                    "tiebreak_points": row.tiebreak_points,
                    "discipline_points": {
                        "snatch": row.snatch_points,
                        "tgu": row.tgu_points,
                        "squat": row.squat_points,
                        "see_saw_press": row.see_saw_press_points,
                        "pistol": row.pistol_points,
                        "pull_up": row.pull_up_points,
                    },
                }
            )
        return output


class SnatchResultSerializer(serializers.Serializer):
    kettlebell_weight = serializers.FloatField(allow_null=True)
    repetitions = serializers.IntegerField(allow_null=True)
    points = serializers.FloatField(allow_null=True)
    place = serializers.IntegerField(allow_null=True)


class AttemptsResultSerializer(serializers.Serializer):
    attempt_1 = serializers.FloatField(allow_null=True)
    attempt_2 = serializers.FloatField(allow_null=True)
    attempt_3 = serializers.FloatField(allow_null=True)
    best_attempt = serializers.FloatField(allow_null=True)
    points = serializers.FloatField(allow_null=True)
    place = serializers.IntegerField(allow_null=True)


class CategoryPlacementSerializer(serializers.ModelSerializer):
    discipline_label = serializers.CharField(source="get_discipline_display", read_only=True)
    player = PlayerSummarySerializer(read_only=True)
    points = serializers.SerializerMethodField()
    tiebreak_applied = serializers.SerializerMethodField()

    class Meta:
        model = CategoryPlacement
        fields = (
            "id",
            "discipline",
            "discipline_label",
            "position",
            "points",
            "tiebreak_applied",
            "player",
        )
        read_only_fields = fields

    def _tiebreak_map(self) -> set[int]:
        return set(self.context.get("tiebreak_players", set()))

    def get_tiebreak_applied(self, obj: CategoryPlacement) -> bool:
        return obj.player_id in self._tiebreak_map()

    def get_points(self, obj: CategoryPlacement) -> float | None:
        return obj.points


class CategoryResultsSerializer(serializers.ModelSerializer):
    player = PlayerSummarySerializer(read_only=True)
    snatch_result = SnatchResultSerializer(source="player.snatch_result", read_only=True)
    tgu_result = serializers.SerializerMethodField()
    squat_result = serializers.SerializerMethodField()
    see_saw_press_result = serializers.SerializerMethodField()
    pistol_result = serializers.SerializerMethodField()
    pull_up_result = serializers.SerializerMethodField()
    discipline_points = serializers.SerializerMethodField()
    discipline_places = serializers.SerializerMethodField()
    placements = serializers.SerializerMethodField()
    tiebreak_applied = serializers.SerializerMethodField()

    class Meta:
        model = CategoryOverallResult
        fields = (
            "id",
            "player",
            "final_position",
            "total_points",
            "discipline_places",
            "placement_points",
            "counted_disciplines",
            "tiebreak_points",
            "tiebreak_applied",
            "discipline_points",
            "placements",
            "snatch_result",
            "tgu_result",
            "squat_result",
            "see_saw_press_result",
            "pistol_result",
            "pull_up_result",
        )
        read_only_fields = fields

    def _attempts_payload(self, obj) -> dict[str, float | None] | None:
        return AttemptsResultSerializer(
            {
                "attempt_1": getattr(obj, "attempt_1", None),
                "attempt_2": getattr(obj, "attempt_2", None),
                "attempt_3": getattr(obj, "attempt_3", None),
                "best_attempt": getattr(obj, "best_attempt", None),
                "points": getattr(obj, "points", None),
            }
        ).data if obj else None

    def get_tgu_result(self, overall: CategoryOverallResult):
        return self._attempts_payload(getattr(overall.player, "tgu_result", None))

    def get_squat_result(self, overall: CategoryOverallResult):
        return self._attempts_payload(getattr(overall.player, "squat_result", None))

    def get_see_saw_press_result(self, overall: CategoryOverallResult):
        return self._attempts_payload(getattr(overall.player, "see_saw_press_result", None))

    def get_pistol_result(self, overall: CategoryOverallResult):
        return self._attempts_payload(getattr(overall.player, "pistol_result", None))

    def get_pull_up_result(self, overall: CategoryOverallResult):
        return self._attempts_payload(getattr(overall.player, "pull_up_result", None))

    def get_discipline_points(self, overall: CategoryOverallResult) -> dict[str, float | None]:
        return {
            "snatch": overall.snatch_points,
            "tgu": overall.tgu_points,
            "squat": overall.squat_points,
            "see_saw_press": overall.see_saw_press_points,
            "pistol": overall.pistol_points,
            "pull_up": overall.pull_up_points,
        }

    def get_discipline_places(self, overall: CategoryOverallResult) -> dict[str, int | None]:
        return {
            "snatch": overall.snatch_place,
            "tgu": overall.tgu_place,
            "squat": overall.squat_place,
            "see_saw_press": overall.see_saw_press_place,
            "pistol": overall.pistol_place,
            "pull_up": overall.pull_up_place,
        }

    def get_tiebreak_applied(self, overall: CategoryOverallResult) -> bool:
        return bool(overall.tiebreak_points)

    def get_placements(self, overall: CategoryOverallResult) -> list[dict[str, object]]:
        placements_map: Mapping[int, Mapping[str, CategoryPlacement]] = self.context.get("placements_map", {})
        category: Category | None = self.context.get("category")
        player_entries = placements_map.get(overall.player_id, {}) if placements_map else {}
        data: list[dict[str, object]] = []
        discipline_order = category.get_disciplines() if isinstance(category, Category) else []

        for code in discipline_order:
            placement: CategoryPlacement | None = player_entries.get(code) if isinstance(player_entries, Mapping) else None
            total_points = getattr(placement, "points", None) if placement else None
            points = total_points if placement is not None else None
            data.append(
                {
                    "discipline": code,
                    "label": DISCIPLINE_NAMES.get(code, code),
                    "position": getattr(placement, "position", None),
                    "points": points,
                }
            )

        return data
