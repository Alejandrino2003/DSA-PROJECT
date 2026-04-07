import tkinter as tk

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER,
    CLR_PRIMARY, CLR_SUCCESS, CLR_WARNING, CLR_OUTLINE,
    CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT,
    CLR_OUTLINE_VARIANT,
)


class AnalyticsMixin:
    """Mixin providing the Analytics tab."""

    def build_analytics_tab(self):
        container = tk.Frame(self.analytics_tab, bg=CLR_SURFACE)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_section_header(container, "Productivity Analytics", "📈", CLR_PRIMARY)

        stats_frame = tk.Frame(container, bg=CLR_SURFACE)
        stats_frame.pack(fill="x", pady=16)

        self.analytics_labels = {}
        stats_items = [
            ("🏆", "Current Level",   "level"),
            ("⭐", "Total XP",        "xp"),
            ("🔥", "Best Streak",     "best_streak"),
            ("✅", "Tasks Completed", "completed_tasks"),
            ("📊", "Completion Rate", "completion_rate"),
            ("🎯", "Weekly Points",   "weekly_points"),
            ("🍅", "Pomodoros",       "pomodoro_count"),
        ]

        for icon, label, key in stats_items:
            card = self.create_card(stats_frame, bg=CLR_SURFACE, border=True)
            card.pack(side="left", fill="both", expand=True, padx=5, pady=4)
            inner = tk.Frame(card, bg=CLR_SURFACE)
            inner.pack(fill="both", expand=True, padx=14, pady=12)
            tk.Label(inner, text=icon, font=("Segoe UI", 18),
                     bg=CLR_SURFACE, fg=CLR_PRIMARY).pack(anchor="w")
            v = tk.Label(inner, text="—",
                         font=("Segoe UI", 20, "bold"),
                         bg=CLR_SURFACE, fg=CLR_PRIMARY)
            v.pack(anchor="w", pady=(2, 0))
            tk.Label(inner, text=label, font=("Segoe UI", 9),
                     bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(anchor="w")
            self.analytics_labels[key] = v

        self.create_section_header(container, "Achievements", "🏅", CLR_SUCCESS)
        self.achievements_frame = tk.Frame(container, bg=CLR_SURFACE_CONTAINER,
                                           highlightthickness=1,
                                           highlightbackground=CLR_OUTLINE_VARIANT)
        self.achievements_frame.pack(fill="x", padx=20, pady=(0, 16))

        self.refresh_analytics()

    def refresh_analytics(self):
        data = self.load_user_data()
        stats = data.get("user_stats", {})
        tasks = data.get("tasks", [])

        completed_tasks = sum(1 for t in tasks if t.get("status") == "Completed")
        total_tasks = len(tasks)
        completion_rate = int(completed_tasks / total_tasks * 100) if total_tasks else 0

        analytics_data = {
            "level":           stats.get("level", 1),
            "xp":              stats.get("xp", 0),
            "best_streak":     stats.get("streak_best", self._calc_streak()),
            "completed_tasks": completed_tasks,
            "completion_rate": f"{completion_rate}%",
            "weekly_points":   stats.get("points_this_week", 0),
            "pomodoro_count":  self.clepsydra_count,
        }

        for key, val in analytics_data.items():
            if key in self.analytics_labels:
                self.analytics_labels[key].config(text=str(val))

        for widget in self.achievements_frame.winfo_children():
            widget.destroy()

        achievements = data.get("achievements", [])
        if achievements:
            for ach in achievements:
                ach_frame = tk.Frame(self.achievements_frame, bg=CLR_SURFACE_CONTAINER)
                ach_frame.pack(fill="x", padx=16, pady=8)
                tk.Label(ach_frame, text="🏆", font=("Segoe UI", 16),
                         bg=CLR_SURFACE_CONTAINER, fg=CLR_WARNING).pack(side="left", padx=(0, 12))
                tk.Label(ach_frame, text=ach.get("name", "Unknown"),
                         font=("Segoe UI", 11, "bold"),
                         bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE).pack(side="left")
                tk.Label(ach_frame, text=ach.get("description", ""),
                         font=("Segoe UI", 9),
                         bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE_VARIANT).pack(side="left", padx=(12, 0))
                tk.Label(ach_frame, text=f"Unlocked: {ach.get('unlocked_at', '')[:10]}",
                         font=("Segoe UI", 8),
                         bg=CLR_SURFACE_CONTAINER, fg=CLR_OUTLINE).pack(side="right")
        else:
            tk.Label(self.achievements_frame,
                     text="No achievements yet. Complete tasks to unlock badges!",
                     font=("Segoe UI", 10), bg=CLR_SURFACE_CONTAINER,
                     fg=CLR_ON_SURFACE_VARIANT).pack(pady=20)