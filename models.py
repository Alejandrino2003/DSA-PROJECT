from datetime import datetime
from constant import DEFAULT_CATEGORIES, DATA_SCHEMA_VER


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _blank_data():
    return {
        "schema_version": DATA_SCHEMA_VER,
        "events":      [],
        "tasks":       [],
        "categories":  list(DEFAULT_CATEGORIES),
        "daily_todos": {},
        "daily_notes": {},
        "habits": [],
        "habit_completions": {},
        "projects": [],
        "daily_reflections": {},
        "time_entries": [],
        "achievements": [],
        "user_stats": {
            "level": 1,
            "xp": 0,
            "streak_best": 0,
            "achievements_unlocked": [],
            "points_this_week": 0
        },
        "timer_settings": {
            "pomodoro_minutes": 25,
            "short_break_minutes": 5,
            "long_break_minutes": 15,
            "auto_break": True
        }
    }


def _migrate(data: dict) -> dict:
    ver = data.get("schema_version", 1)
    if ver < 2:
        for ev in data.get("events", []):
            ev.setdefault("tags", [])
            ev.setdefault("category", "Work")
            ev.setdefault("recurrence", "none")
            ev.setdefault("created_at", _now_iso())
            ev.setdefault("updated_at", _now_iso())
        for t in data.get("tasks", []):
            t.setdefault("tags", [])
            t.setdefault("category", "Work")
            t.setdefault("created_at", _now_iso())
            t.setdefault("updated_at", _now_iso())
        for day_list in data.get("daily_todos", {}).values():
            for td in day_list:
                td.setdefault("tags", [])
                td.setdefault("created_at", _now_iso())
        data.setdefault("daily_notes", {})
        data["schema_version"] = 2
    if ver < 3:
        data.setdefault("habits", [])
        data.setdefault("habit_completions", {})
        data.setdefault("projects", [])
        data.setdefault("daily_reflections", {})
        data.setdefault("time_entries", [])
        data.setdefault("achievements", [])
        data.setdefault("user_stats", {
            "level": 1, "xp": 0, "streak_best": 0,
            "achievements_unlocked": [], "points_this_week": 0
        })
        data.setdefault("timer_settings", {
            "pomodoro_minutes": 25,
            "short_break_minutes": 5,
            "long_break_minutes": 15,
            "auto_break": True
        })
        for t in data.get("tasks", []):
            t.setdefault("quadrant", "Q2: Schedule")
            t.setdefault("importance", "Medium")
            t.setdefault("urgency", "Medium")
            t.setdefault("project_id", None)
            t.setdefault("estimated_minutes", 0)
            t.setdefault("actual_minutes", 0)
        data["schema_version"] = 3
    return data