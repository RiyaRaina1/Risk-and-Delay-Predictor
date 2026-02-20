from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

@dataclass
class RiskResult:
    risk_score: int               # 0..100
    risk_level: str               # LOW/MED/HIGH
    reasons: List[str]            # explainable reasons
    kpis: Dict[str, Any]          # computed KPIs

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def compute_kpis(planned: int, completed: int, in_progress: int,
                 blockers: int, bugs_open: int, scope_change: float, cycle_time: float) -> Dict[str, Any]:
    planned = max(planned, 0)
    completed = max(completed, 0)
    in_progress = max(in_progress, 0)
    blockers = max(blockers, 0)
    bugs_open = max(bugs_open, 0)
    scope_change = clamp(scope_change, 0.0, 100.0)
    cycle_time = max(cycle_time, 0.0)

    completion_rate = (completed / planned) if planned > 0 else 0.0
    remaining = max(planned - completed, 0)

    return {
        "completion_rate": round(completion_rate, 3),   # 0..1
        "remaining_tasks": remaining,
        "blockers": blockers,
        "bugs_open": bugs_open,
        "scope_change_percent": round(scope_change, 2),
        "avg_cycle_time_days": round(cycle_time, 2),
    }

def risk_score_engine(current: Dict[str, Any], prev: Dict[str, Any] | None) -> RiskResult:
    """
    Explainable risk scoring (0-100).
    Uses current snapshot and optional previous snapshot for trend (velocity drop).
    """
    planned = int(current["planned_tasks"])
    completed = int(current["completed_tasks"])
    in_progress = int(current["in_progress_tasks"])
    blockers = int(current["blockers_count"])
    bugs_open = int(current["bugs_open"])
    scope_change = float(current["scope_change_percent"])
    cycle_time = float(current["avg_cycle_time_days"])

    kpis = compute_kpis(planned, completed, in_progress, blockers, bugs_open, scope_change, cycle_time)

    score = 0.0
    reasons: List[str] = []

    # 1) Low completion rate is a strong risk signal
    cr = kpis["completion_rate"]  # 0..1
    if planned > 0:
        # risk contribution: 0 when >=0.9, high when low
        completion_risk = clamp((0.9 - cr) / 0.9, 0.0, 1.0) * 35
        score += completion_risk
        if cr < 0.6:
            reasons.append(f"Low completion rate ({cr*100:.0f}%) vs planned tasks.")
        elif cr < 0.8:
            reasons.append(f"Moderate completion rate ({cr*100:.0f}%)—schedule pressure possible.")

    # 2) Blockers directly increase delay probability
    blocker_risk = clamp(blockers / 5.0, 0.0, 1.0) * 15
    score += blocker_risk
    if blockers >= 3:
        reasons.append(f"High blockers count ({blockers}) slowing progress.")
    elif blockers >= 1:
        reasons.append(f"Some blockers present ({blockers}).")

    # 3) Bugs open affects quality + rework time
    bug_risk = clamp(bugs_open / 20.0, 0.0, 1.0) * 15
    score += bug_risk
    if bugs_open >= 10:
        reasons.append(f"High number of open bugs ({bugs_open}) causing rework.")
    elif bugs_open >= 4:
        reasons.append(f"Open bugs ({bugs_open}) may slow delivery.")

    # 4) Scope change is a classic delay driver
    scope_risk = clamp(scope_change / 30.0, 0.0, 1.0) * 15
    score += scope_risk
    if scope_change >= 15:
        reasons.append(f"Scope increased by {scope_change:.0f}%—delivery risk increased.")
    elif scope_change >= 5:
        reasons.append(f"Scope change of {scope_change:.0f}% detected.")

    # 5) Cycle time rising = slower throughput
    cycle_risk = clamp((cycle_time - 2.0) / 5.0, 0.0, 1.0) * 10   # no risk until ~2 days
    score += cycle_risk
    if cycle_time >= 5:
        reasons.append(f"High average cycle time ({cycle_time:.1f} days).")

    # 6) Trend: velocity drop compared to previous snapshot (if present)
    if prev:
        prev_planned = int(prev["planned_tasks"])
        prev_completed = int(prev["completed_tasks"])
        prev_cr = (prev_completed / prev_planned) if prev_planned > 0 else 0.0

        if prev_cr > 0 and cr < prev_cr:
            drop = prev_cr - cr
            trend_risk = clamp(drop / 0.5, 0.0, 1.0) * 10
            score += trend_risk
            reasons.append(f"Velocity drop: completion rate decreased from {prev_cr*100:.0f}% to {cr*100:.0f}%.")

    # Normalize
    score = int(round(clamp(score, 0, 100)))

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    if not reasons:
        reasons.append("Metrics look stable. Low risk signals detected.")

    return RiskResult(risk_score=score, risk_level=level, reasons=reasons, kpis=kpis)