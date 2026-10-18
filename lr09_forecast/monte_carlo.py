#!/usr/bin/env python3
"""Скрипт симуляції Монте-Карло для прогнозу кількості спринтів (ЛР9)."""

import csv
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

SEED = 42
SIMULATIONS = 10000
SPRINT_LENGTH_DAYS = 14


def simulate_sprints(velocities: list[int], remaining_points: int, n_sims: int = SIMULATIONS, seed: int = SEED):
    """Проганяє n_sims симуляцій Монте-Карло з поверненням і рахує P50, P85, P95 та розподіл."""
    rng = random.Random(seed)
    outcomes = []
    for _ in range(n_sims):
        rem = remaining_points
        sprints = 0
        while rem > 0:
            rem -= rng.choice(velocities)
            sprints += 1
        outcomes.append(sprints)
    outcomes.sort()
    p50 = outcomes[int(0.50 * n_sims) - 1]
    p85 = outcomes[int(0.85 * n_sims) - 1]
    p95 = outcomes[int(0.95 * n_sims) - 1]
    counts = Counter(outcomes)
    return p50, p85, p95, counts


def load_velocities(csv_path: Path) -> tuple[list[int], date, date]:
    velocities = []
    first_start = None
    last_end = None
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            velocities.append(int(row["points_done"]))
            s_date = date.fromisoformat(row["start_date"])
            e_date = date.fromisoformat(row["end_date"])
            if first_start is None or s_date < first_start:
                first_start = s_date
            if last_end is None or e_date > last_end:
                last_end = e_date
    return velocities, first_start, last_end


def main():
    here = Path(__file__).resolve().parent
    vel_path = here / "velocity.csv"
    velocities, first_start, last_end = load_velocities(vel_path)

    print(f"Власна історія velocity ({vel_path.name}): {velocities}")
    print(f"Середній темп: {sum(velocities) / len(velocities):.2f} SP/спринт\n")

    for name, points, base_date in [
        ("Весь перший реліз", 90, date(2026, 9, 18)),  # п'ятниця перед стартом Спринта 1 для 14-денної сітки п'ятниць
        ("Залишок після двох спринтів", 60, last_end),
    ]:
        p50, p85, p95, counts = simulate_sprints(velocities, points)
        d50 = base_date + timedelta(days=p50 * SPRINT_LENGTH_DAYS)
        d85 = base_date + timedelta(days=p85 * SPRINT_LENGTH_DAYS)
        print(f"=== Сценарій: {name} ({points} SP) ===")
        print(f"P50 = {p50} спр. ({d50}), P85 = {p85} спр. ({d85}), P95 = {p95} спр.")
        cum = 0
        for s in sorted(counts):
            cum += counts[s]
            print(f"  {s:2d} спринтів: {counts[s]:4d} прогонів ({counts[s]/SIMULATIONS*100:5.2f}%), накопичена {cum/SIMULATIONS*100:6.2f}%")
        print()


if __name__ == "__main__":
    main()
