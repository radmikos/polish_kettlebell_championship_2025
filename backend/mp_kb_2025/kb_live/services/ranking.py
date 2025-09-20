"""Utilities for recomputing and ranking overall category results."""

from __future__ import annotations

import math
from typing import Iterable

from kb_live.models import CategoryOverallResult


def rank_category_overall(category_id: int, player_ids: Iterable[int] | None = None) -> int:
    """Recompute ordering for a category and assign final positions.

    Returns the number of records updated.
    """

    qs = CategoryOverallResult.objects.filter(category_id=category_id).select_related("player")
    if player_ids is not None:
        qs = qs.filter(player_id__in=set(player_ids))

    rows = list(qs)
    if not rows:
        return 0

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
