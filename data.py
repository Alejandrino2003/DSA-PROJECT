"""
VIAM CENTRIC - Data Persistence (Load / Save User Data)
"""

import json
from constant import DATA_SCHEMA_VER
from models import _blank_data, _migrate


class DataMixin:
    """Mixin providing user data load/save methods."""

    def user_data_path(self):
        safe = "".join(c if c.isalnum() else "_"
                       for c in self.current_user["username"].lower())
        return self.data_dir / f"{safe}.json"

    def load_user_data(self) -> dict:
        path = self.user_data_path()
        if not path.exists():
            return _blank_data()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data = _migrate(data)
            blank = _blank_data()
            for k in blank:
                data.setdefault(k, blank[k])
            # Load timer settings from user data
            timer_settings = data.get("timer_settings", {})
            self.clepsydra_duration = timer_settings.get("clepsydra_minutes", 25) * 60
            self.short_break_duration = timer_settings.get("short_break_minutes", 5) * 60
            self.long_break_duration = timer_settings.get("long_break_minutes", 15) * 60
            self.clepsydra_auto_break = timer_settings.get("auto_break", True)
            return data
        except:
            return _blank_data()

    def save_user_data(self, data: dict):
        # Save current timer settings
        if "timer_settings" not in data:
            data["timer_settings"] = {}
        data["timer_settings"]["clepsydra_minutes"] = self.clepsydra_duration // 60
        data["timer_settings"]["short_break_minutes"] = self.short_break_duration // 60
        data["timer_settings"]["long_break_minutes"] = self.long_break_duration // 60
        data["timer_settings"]["auto_break"] = self.clepsydra_auto_break
        data["schema_version"] = DATA_SCHEMA_VER
        with open(self.user_data_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def next_id(items):
        return max((i.get("id", 0) for i in items
                    if isinstance(i.get("id"), int)), default=0) + 1

    @staticmethod
    def date_part(s):
        if not s:
            return ""
        return s[:10] if len(s) >= 10 else s