"""Recurrence calculator — computes next occurrence dates."""

import calendar
from datetime import datetime, timedelta, timezone
from typing import Any


def compute_next_occurrence(
    completed_at: datetime,
    recurrence_pattern: dict[str, Any],
) -> datetime:
    """Compute the next occurrence date based on the recurrence pattern.

    Args:
        completed_at: When the current occurrence was completed.
        recurrence_pattern: JSONB pattern with 'type' and type-specific fields.

    Returns:
        The next due date as a timezone-aware datetime.

    Raises:
        ValueError: If the pattern type is unknown or invalid.
    """
    rtype = recurrence_pattern.get("type")

    if rtype == "daily":
        return completed_at + timedelta(days=1)

    elif rtype == "weekly":
        days_of_week = recurrence_pattern.get("days_of_week", [])
        if not days_of_week:
            raise ValueError("Weekly recurrence requires 'days_of_week'")

        # days_of_week: 0=Mon, 6=Sun (Python weekday convention)
        current_dow = completed_at.weekday()
        sorted_days = sorted(days_of_week)

        # Find the next day that's after today
        for day in sorted_days:
            if day > current_dow:
                delta = day - current_dow
                return completed_at + timedelta(days=delta)

        # Wrap to next week
        first_day = sorted_days[0]
        delta = 7 - current_dow + first_day
        return completed_at + timedelta(days=delta)

    elif rtype == "monthly":
        day_of_month = recurrence_pattern.get("day_of_month")
        if day_of_month is None:
            raise ValueError("Monthly recurrence requires 'day_of_month'")

        # Move to next month
        year = completed_at.year
        month = completed_at.month + 1
        if month > 12:
            month = 1
            year += 1

        # Clamp to valid day for the target month
        max_day = calendar.monthrange(year, month)[1]
        actual_day = min(day_of_month, max_day)

        return completed_at.replace(
            year=year, month=month, day=actual_day
        )

    elif rtype == "custom":
        interval_days = recurrence_pattern.get("interval_days")
        if not interval_days or interval_days < 1:
            raise ValueError("Custom recurrence requires 'interval_days' >= 1")
        return completed_at + timedelta(days=interval_days)

    else:
        raise ValueError(f"Unknown recurrence type: {rtype}")
