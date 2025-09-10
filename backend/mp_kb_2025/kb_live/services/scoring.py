from dataclasses import dataclass
from typing import Optional
import math

@dataclass(frozen=True)
class Context:
    weight: float           # masa ciała (kg) > 0
    gender: str             # 'female' lub 'male'

def _round_to_half(x: float) -> float:
    return math.floor((x + 0.25) / 0.5) * 0.5

def snatch_points(ctx: Context, kb: float, reps: int) -> Optional[float]:
    if kb <= 0 or reps <= 0 or ctx.weight <= 0 or ctx.gender not in {"female", "male"}:
        return None
    body_pow = ctx.weight ** 0.4
    if ctx.gender == "female":
        ref_pow, denom = 65 ** 0.4, 16
    else:
        ref_pow, denom = 85 ** 0.4, 24
    raw = (reps * kb) / body_pow * (ref_pow / denom)
    return _round_to_half(raw)

def pistol_points(ctx: Context, kb: float) -> Optional[float]:
    if kb <= 0 or ctx.weight <= 0 or ctx.gender not in {"female", "male"}:
        return None
    if ctx.gender == "female":
        return (kb / (ctx.weight ** 0.6)) * ((65 ** 0.6) / 40)
    return (kb / (ctx.weight ** 0.67)) * ((85 ** 0.67) / 60)

def see_saw_points(ctx: Context, kb_sum: float) -> Optional[float]:
    if kb_sum <= 0 or ctx.weight <= 0 or ctx.gender not in {"female", "male"}:
        return None
    if ctx.gender == "female":
        return (kb_sum / (ctx.weight ** 0.6)) * ((65 ** 0.6) / 48)
    return (kb_sum / (ctx.weight ** 0.67)) * ((85 ** 0.67) / 96)

def squat_points(ctx: Context, kb_sum: float) -> Optional[float]:
    if kb_sum <= 0 or ctx.weight <= 0 or ctx.gender not in {"female", "male"}:
        return None
    if ctx.gender == "female":
        return (kb_sum / (ctx.weight ** 0.6)) * ((65 ** 0.6) / 72)
    return (kb_sum / (ctx.weight ** 0.67)) * ((85 ** 0.67) / 120)

def tgu_points(ctx: Context, kb: float) -> Optional[float]:
    if kb <= 0 or ctx.weight <= 0 or ctx.gender not in {"female", "male"}:
        return None
    if ctx.gender == "female":
        return (kb / (ctx.weight ** 0.6)) * ((65 ** 0.6) / 48)
    return (kb / (ctx.weight ** 0.67)) * ((85 ** 0.67) / 80)

def pull_up_points(ctx: Context, added_weight: float) -> Optional[float]:
    if ctx.weight <= 0 or ctx.gender not in {"female", "male"}:
        return None
    final_w = ctx.weight + max(0.0, added_weight)
    if final_w <= 0:
        return None
    if ctx.gender == "female":
        return (final_w / (ctx.weight ** 0.6)) * ((65 ** 0.6) / 100)
    return (final_w / (ctx.weight ** 0.67)) * ((85 ** 0.67) / 150)
