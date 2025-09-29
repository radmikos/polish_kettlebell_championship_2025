"""Utilities for recomputing per-discipline and overall rankings."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Sequence

from kb_live.models import CategoryOverallResult, CategoryPlacement


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


def rank_category_disciplines(category_id: int, disciplines: Iterable[str] | None = None) -> set[int]:
    """Recompute per-discipline positions for all placements in the category."""

    placements_qs = CategoryPlacement.objects.filter(category_id=category_id)
    if disciplines is not None:
        discipline_list = list(disciplines)
        if not discipline_list:
            return set()
        placements_qs = placements_qs.filter(discipline__in=discipline_list)

    placements = placements_qs.select_related("player", "category")
    rows = list(placements)
    if not rows:
        return set()

    grouped: dict[str, list[CategoryPlacement]] = defaultdict(list)
    for row in rows:
        grouped[row.discipline].append(row)

    to_update: list[CategoryPlacement] = []
    affected_players: set[int] = set()

    for discipline, discipline_rows in grouped.items():
        ordered = _sorted_rows_for_discipline(discipline_rows)
        prev_points = None
        current_place = 0

        for idx, row in enumerate(ordered, start=1):
            pts = row.points
            if pts is None:
                if row.position is not None:
                    row.position = None
                    to_update.append(row)
                continue

            if prev_points is None or not math.isclose(pts, prev_points, rel_tol=1e-9, abs_tol=1e-9):
                current_place = idx
                prev_points = pts

            if row.position != current_place:
                row.position = current_place
                to_update.append(row)
                affected_players.add(row.player_id)

    if to_update:
        CategoryPlacement.objects.bulk_update(to_update, ["position"])

    return affected_players


def rank_category_overall(category_id: int, player_ids: Iterable[int] | None = None) -> int:
    """Recompute ordering for a category and assign final positions."""

    rank_category_disciplines(category_id)

    qs = CategoryOverallResult.objects.filter(category_id=category_id).select_related("player")
    if player_ids is not None:
        qs = qs.filter(player_id__in=set(player_ids))

    rows = list(qs)
    if not rows:
        return 0

    rows.sort(
        key=lambda r: (
            r.counted_disciplines == 0,
            float("inf") if r.placement_points is None else r.placement_points,
            -(r.total_points or 0.0),
            getattr(r.player, "surname", ""),
            getattr(r.player, "name", ""),
        )
    )

    prev_points = None
    current_rank = 0
    for idx, row in enumerate(rows, start=1):
        if row.counted_disciplines == 0 or row.placement_points is None:
            row.final_position = None
            continue
        if prev_points is None or not math.isclose(row.placement_points, prev_points, rel_tol=1e-9, abs_tol=1e-9):
            current_rank = idx
            prev_points = row.placement_points
        row.final_position = current_rank

    CategoryOverallResult.objects.bulk_update(rows, ["final_position"])
    return len(rows)
