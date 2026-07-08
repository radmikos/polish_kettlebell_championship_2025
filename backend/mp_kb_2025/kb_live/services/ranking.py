"""Utilities for recomputing per-discipline and overall rankings."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Sequence

from kb_live.models import (
    Category,
    CategoryOverallResult,
    CategoryPlacement,
    Discipline,
    PistolResult,
    Player,
    PullUpResult,
    SeeSawPressResult,
    SnatchResult,
    SquatResult,
    TGUResult,
)


def _sorted_rows_for_discipline(rows: Sequence[CategoryPlacement]) -> list[CategoryPlacement]:
    return sorted(
        rows,
        key=lambda r: (
            r.points is None,
            -float(r.points) if r.points is not None else 0.0,
            getattr(r.player, "surname", ""),
            getattr(r.player, "name", ""),
            r.player_id or 0,
        ),
    )


RESULT_ATTR_MODEL_MAP = {
    Discipline.SNATCH: ("snatch_result", SnatchResult),
    Discipline.TGU: ("tgu_result", TGUResult),
    Discipline.SQUAT: ("squat_result", SquatResult),
    Discipline.SEE_SAW_PRESS: ("see_saw_press_result", SeeSawPressResult),
    Discipline.PISTOL: ("pistol_result", PistolResult),
    Discipline.PULL_UP: ("pull_up_result", PullUpResult),
}


def rank_category_disciplines(category_id: int, disciplines: Iterable[str] | None = None) -> set[int]:
    """Recompute per-discipline positions for placements and result models."""

    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return set()

    placements_qs = CategoryPlacement.objects.filter(category_id=category_id)
    if disciplines is not None:
        discipline_list = list(disciplines)
        if not discipline_list:
            return set()
        placements_qs = placements_qs.filter(discipline__in=discipline_list)

    placements = placements_qs.select_related("player", "category")
    rows = list(placements)

    allowed_codes = set(category.get_disciplines() or [])
    target_disciplines = set(disciplines) if disciplines is not None else set(allowed_codes)
    target_disciplines &= set(RESULT_ATTR_MODEL_MAP.keys())
    target_disciplines &= allowed_codes

    existing_pairs = {(p.player_id, p.discipline) for p in rows if p.player_id}
    new_placements: list[CategoryPlacement] = []
    affected_players: set[int] = set()

    if target_disciplines:
        player_select = [
            "snatch_result",
            "tgu_result",
            "squat_result",
            "see_saw_press_result",
            "pistol_result",
            "pull_up_result",
        ]
        players = (
            Player.objects.filter(categories__id=category_id)
            .select_related(*player_select)
            .distinct()
        )
        for player in players:
            for discipline in target_disciplines:
                pair = (player.pk, discipline)
                if pair in existing_pairs:
                    continue
                placement = CategoryPlacement(
                    category=category,
                    player=player,
                    discipline=discipline,
                )
                new_placements.append(placement)
                existing_pairs.add(pair)
                affected_players.add(player.pk)

    if new_placements:
        CategoryPlacement.objects.bulk_create(new_placements, ignore_conflicts=True)
        rows.extend(new_placements)

    if not rows:
        return affected_players

    grouped: dict[str, list[CategoryPlacement]] = defaultdict(list)
    for row in rows:
        grouped[row.discipline].append(row)

    to_update: list[CategoryPlacement] = []
    result_updates: dict[type, dict[int, object]] = defaultdict(dict)

    for discipline, discipline_rows in grouped.items():
        ordered = _sorted_rows_for_discipline(discipline_rows)
        prev_points = None
        current_place = 0
        no_points_place: int | None = None

        for idx, row in enumerate(ordered, start=1):
            pts = row.points
            if pts is None:
                if current_place == 0:
                    target_place = 1
                else:
                    if no_points_place is None:
                        no_points_place = current_place + 1
                    target_place = no_points_place

                if row.position != target_place:
                    row.position = target_place
                    to_update.append(row)
                    if row.player_id:
                        affected_players.add(row.player_id)

                attr_model = RESULT_ATTR_MODEL_MAP.get(discipline)
                if attr_model:
                    attr_name, model = attr_model
                    result = getattr(row.player, attr_name, None)
                    if result and result.place != target_place:
                        result.place = target_place
                        result_updates[model][result.pk] = result
                continue

            if prev_points is None or not math.isclose(pts, prev_points, rel_tol=1e-9, abs_tol=1e-9):
                current_place = idx
                prev_points = pts

            if row.position != current_place:
                row.position = current_place
                to_update.append(row)
                if row.player_id:
                    affected_players.add(row.player_id)

            attr_model = RESULT_ATTR_MODEL_MAP.get(discipline)
            if attr_model:
                attr_name, model = attr_model
                result = getattr(row.player, attr_name, None)
                if result and result.place != current_place:
                    result.place = current_place
                    result_updates[model][result.pk] = result

    if to_update:
        placement_updates = [row for row in to_update if getattr(row, "pk", None)]
        if placement_updates:
            CategoryPlacement.objects.bulk_update(placement_updates, ["position"])

    for model, instances_map in result_updates.items():
        if instances_map:
            result_list = [instance for instance in instances_map.values() if getattr(instance, "pk", None)]
            if result_list:
                model.objects.bulk_update(result_list, ["place"])

    return affected_players


def rank_category_overall(
    category_id: int,
    player_ids: Iterable[int] | None = None,
    *,
    recompute_disciplines: bool = True,
) -> int:
    """Recompute ordering for a category and assign final positions."""

    if recompute_disciplines:
        rank_category_disciplines(category_id)

    qs = CategoryOverallResult.objects.filter(category_id=category_id).select_related("player")
    if player_ids is not None:
        qs = qs.filter(player_id__in=set(player_ids))

    rows = list(qs)
    if not rows:
        return 0

    for row in rows:
        row.recompute(save=True)

    rows.sort(
        key=lambda r: (
            r.counted_disciplines == 0,
            float("inf") if r.total_points is None else r.total_points,
            getattr(r.player, "surname", ""),
            getattr(r.player, "name", ""),
        )
    )

    prev_points = None
    current_rank = 0
    for idx, row in enumerate(rows, start=1):
        if row.counted_disciplines == 0 or row.total_points is None:
            row.final_position = None
            continue
        if prev_points is None or not math.isclose(row.total_points, prev_points, rel_tol=1e-9, abs_tol=1e-9):
            current_rank = idx
            prev_points = row.total_points
        row.final_position = current_rank

    CategoryOverallResult.objects.bulk_update(rows, ["final_position"])
    return len(rows)
