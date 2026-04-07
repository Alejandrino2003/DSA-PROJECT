import tkinter as tk
from datetime import datetime

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER, CLR_SURFACE_CONTAINER_HIGH,
    CLR_PRIMARY, CLR_PRIMARY_FIXED, CLR_ON_PRIMARY,
    CLR_SECONDARY, CLR_TERTIARY, CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT,
    CLR_ERROR, CLR_ERROR_CONTAINER, CLR_SUCCESS, CLR_WARNING, CLR_OUTLINE,
    CLR_OUTLINE_VARIANT, QUOTES,
)
from models import _now_iso


class DashboardMixin:
    """Mixin providing the Dashboard tab build and refresh logic."""

    def build_dashboard(self):
        _, container = self._scrollable(self.dashboard_tab)

        hdr = tk.Frame(container, bg=CLR_SURFACE)
        hdr.pack(fill="x", padx=24, pady=(20, 16))
        tk.Label(hdr, text="VIAM DASHBOARD",
                 font=("Sans-serif", 28, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE).pack(side="left")
        self.create_button(hdr, "⟳ Refresh",
                           self.refresh_dashboard,
                           primary=False).pack(side="right")

        # Stats cards
        stats_frame = tk.Frame(container, bg=CLR_SURFACE)
        stats_frame.pack(fill="x", padx=20, pady=(0, 16))
        self.stat_labels = {}
        for icon, label, color in [
            ("📋", "Total Tasks",   CLR_PRIMARY),
            ("✅", "Completed",     CLR_SUCCESS),
            ("⏳", "Pending",       CLR_WARNING),
            ("🔴", "Overdue",       CLR_ERROR),
            ("📅", "Events",        CLR_SECONDARY),
            ("🎯", "Habits",        "#8b5cf6"),
        ]:
            card = self.create_card(stats_frame, bg=CLR_SURFACE, border=True)
            card.pack(side="left", fill="both", expand=True, padx=5, pady=4)
            inner = tk.Frame(card, bg=CLR_SURFACE)
            inner.pack(fill="both", expand=True, padx=14, pady=12)
            tk.Label(inner, text=icon, font=("Segoe UI", 18),
                     bg=CLR_SURFACE, fg=color).pack(anchor="w")
            v = tk.Label(inner, text="—",
                         font=("Segoe UI", 26, "bold"),
                         bg=CLR_SURFACE, fg=color)
            v.pack(anchor="w", pady=(2, 0))
            tk.Label(inner, text=label, font=("Segoe UI", 9),
                     bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(anchor="w")
            self.stat_labels[label] = v

        # Priority Matrix (Eisenhower)
        eisenhower_frame = tk.Frame(container, bg=CLR_SURFACE)
        eisenhower_frame.pack(fill="x", padx=20, pady=(0, 16))
        self.create_section_header(eisenhower_frame, " Priority Matrix", "🎯", CLR_PRIMARY)
        matrix_frame = tk.Frame(eisenhower_frame, bg=CLR_SURFACE)
        matrix_frame.pack(fill="x", padx=20, pady=(0, 16))
        quadrants = ["Q1: Do First", "Q2: Schedule", "Q3: Delegate", "Q4: Eliminate"]
        colors = [CLR_ERROR, CLR_SUCCESS, CLR_WARNING, CLR_OUTLINE]
        self.quadrant_labels = {}
        for i, (quad, color) in enumerate(zip(quadrants, colors)):
            row, col = i // 2, i % 2
            frame = tk.Frame(matrix_frame, bg=color, highlightthickness=1,
                             highlightbackground=CLR_OUTLINE_VARIANT)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            matrix_frame.grid_columnconfigure(col, weight=1)
            matrix_frame.grid_rowconfigure(row, weight=1)
            tk.Label(frame, text=quad, font=("Segoe UI", 10, "bold"),
                     bg=color, fg=CLR_ON_PRIMARY).pack(pady=8)
            listbox = tk.Listbox(frame, height=6, font=("Segoe UI", 9),
                                 bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE,
                                 selectbackground=CLR_PRIMARY_FIXED,
                                 relief=tk.FLAT, highlightthickness=0)
            listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
            self.quadrant_labels[quad] = listbox

        # Progress ring + overdue
        mid = tk.Frame(container, bg=CLR_SURFACE)
        mid.pack(fill="x", padx=20, pady=(0, 16))

        ring_card = self.create_card(mid, bg=CLR_PRIMARY, border=False)
        ring_card.pack(side="left", padx=6, pady=4)
        tk.Label(ring_card, text="Completion Rate",
                 font=("Segoe UI", 12, "bold"),
                 bg=CLR_PRIMARY, fg=CLR_ON_PRIMARY).pack(pady=(20, 8))
        self.ring_canvas = tk.Canvas(ring_card, width=120, height=120,
                                      bg=CLR_PRIMARY, highlightthickness=0)
        self.ring_canvas.pack(pady=8)
        self.completion_label = tk.Label(ring_card, text="0%",
                                          font=("Segoe UI", 24, "bold"),
                                          bg=CLR_PRIMARY, fg=CLR_ON_PRIMARY)
        self.completion_label.pack(pady=(0, 20))

        overdue_card = self.create_card(mid, bg=CLR_SURFACE, border=True)
        overdue_card.pack(side="left", fill="both", expand=True, padx=6, pady=4)
        self.create_section_header(overdue_card, "Overdue / Due Today", "⚠️", CLR_ERROR)
        self.overdue_listbox = tk.Listbox(
            overdue_card, height=8, font=("Segoe UI", 9),
            bg=CLR_ERROR_CONTAINER, fg=CLR_ON_SURFACE,
            selectbackground=CLR_PRIMARY_FIXED,
            relief=tk.FLAT, highlightthickness=0)
        self.overdue_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Work / Personal split
        lists_frame = tk.Frame(container, bg=CLR_SURFACE)
        lists_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        work_card = self.create_card(lists_frame, bg=CLR_SURFACE, border=True)
        work_card.pack(side="left", fill="both", expand=True, padx=6)
        self.create_section_header(work_card, "Work Tasks", "💼", CLR_PRIMARY)
        self.work_tasks_listbox = tk.Listbox(
            work_card, height=8, font=("Segoe UI", 10),
            bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE,
            selectbackground=CLR_PRIMARY_FIXED,
            relief=tk.FLAT, highlightthickness=0)
        self.work_tasks_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        personal_card = self.create_card(lists_frame, bg=CLR_SURFACE, border=True)
        personal_card.pack(side="left", fill="both", expand=True, padx=6)
        self.create_section_header(personal_card, "Personal Tasks", "🏃", CLR_SECONDARY)
        self.personal_tasks_listbox = tk.Listbox(
            personal_card, height=8, font=("Segoe UI", 10),
            bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE,
            selectbackground=CLR_PRIMARY_FIXED,
            relief=tk.FLAT, highlightthickness=0)
        self.personal_tasks_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Timer Section
        pomo_frame = tk.Frame(container, bg=CLR_SURFACE)
        pomo_frame.pack(fill="x", padx=20, pady=(0, 16))

        pomo_header = tk.Frame(pomo_frame, bg=CLR_SURFACE)
        pomo_header.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(pomo_header, text="VIAM Timer", font=("Segoe UI", 13, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE).pack(side="left")
        self.create_button(pomo_header, "⚙ Settings", self.show_timer_settings,
                           primary=False, width=10).pack(side="right")

        timer_card = self.create_card(pomo_frame, bg=CLR_SURFACE_CONTAINER_HIGH, border=True)
        timer_card.pack(fill="x", padx=20, pady=(0, 16))

        mode_frame = tk.Frame(timer_card, bg=CLR_SURFACE_CONTAINER_HIGH)
        mode_frame.pack(pady=(16, 8))
        self.create_button(mode_frame, "🍅 clepsydra",
                           lambda: self.switch_timer_mode("clepsydra"),
                           primary=False, width=12).pack(side="left", padx=5)
        self.create_button(mode_frame, "☕ Short Break",
                           lambda: self.switch_timer_mode("short_break"),
                           primary=False, width=12).pack(side="left", padx=5)
        self.create_button(mode_frame, "🌿 Long Break",
                           lambda: self.switch_timer_mode("long_break"),
                           primary=False, width=12).pack(side="left", padx=5)

        preset_frame = tk.Frame(timer_card, bg=CLR_SURFACE_CONTAINER_HIGH)
        preset_frame.pack(pady=(0, 8))
        tk.Label(preset_frame, text="Quick Presets:", font=("Segoe UI", 9),
                 bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE_VARIANT).pack(side="left", padx=(0, 10))
        for label, minutes in [("5m", 5), ("10m", 10), ("15m", 15), ("20m", 20), ("30m", 30), ("45m", 45)]:
            self.create_button(preset_frame, label,
                               lambda m=minutes: self.set_custom_timer(m),
                               primary=False, width=4).pack(side="left", padx=2)

        self.timer_display = tk.Label(timer_card, text="25:00",
                                       font=("Segoe UI", 48, "bold"),
                                       bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_PRIMARY)
        self.timer_display.pack(pady=20)

        timer_buttons = tk.Frame(timer_card, bg=CLR_SURFACE_CONTAINER_HIGH)
        timer_buttons.pack(pady=(0, 20))
        self.timer_start_btn = self.create_button(timer_buttons, "▶ Start", self.start_clepsydra,
                                                   primary=True, width=10)
        self.timer_start_btn.pack(side="left", padx=5)
        self.create_button(timer_buttons, "⏸ Pause", self.pause_clepsydra,
                           primary=False, width=10).pack(side="left", padx=5)
        self.create_button(timer_buttons, "⏹ Reset", self.reset_clepsydra,
                           primary=False, width=10).pack(side="left", padx=5)

        self.session_label = tk.Label(timer_card,
                                       text=f"Sessions completed: {self.clepsydra_count}",
                                       font=("Segoe UI", 9),
                                       bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE_VARIANT)
        self.session_label.pack(pady=(0, 16))

        # Quote bar
        qf = tk.Frame(container, bg=CLR_PRIMARY_FIXED)
        qf.pack(fill="x", padx=20, pady=(0, 20))
        self.quote_label = tk.Label(qf, text="",
                                     font=("Segoe UI", 10, "italic"),
                                     bg=CLR_PRIMARY_FIXED, fg=CLR_PRIMARY,
                                     wraplength=800)
        self.quote_label.pack(pady=16, padx=20)

        self.refresh_dashboard()

    def _calc_stats(self):
        data = self.load_user_data()
        tasks = data.get("tasks", [])
        events = data.get("events", [])
        habits = data.get("habits", [])
        today = datetime.now().date()
        total     = len(tasks)
        completed = sum(1 for t in tasks if t.get("status") == "Completed")
        pending   = sum(1 for t in tasks if t.get("status") != "Completed")
        overdue   = sum(1 for t in tasks
                        if t.get("status") != "Completed"
                        and self.date_part(t.get("due_date", "")) < today.isoformat())
        today_str = today.isoformat()
        completions = data.get("habit_completions", {}).get(today_str, [])
        habit_complete = len([h for h in habits if h.get("id") in completions])
        habit_total = len(habits) if habits else 1
        return {
            "total_tasks": total, "completed": completed,
            "pending": pending, "overdue": overdue,
            "total_events": len(events),
            "habit_completion": int(habit_complete / habit_total * 100) if habit_total else 0,
            "rate": int(completed / total * 100) if total else 0,
            "tasks": tasks, "events": events,
            "daily_todos": data.get("daily_todos", {}),
        }

    def refresh_dashboard(self):
        s = self._calc_stats()
        mapping = {
            "Total Tasks": s["total_tasks"],
            "Completed":   s["completed"],
            "Pending":     s["pending"],
            "Overdue":     s["overdue"],
            "Events":      s["total_events"],
            "Habits":      f"{s['habit_completion']}%",
        }
        for label, val in mapping.items():
            if label in self.stat_labels:
                self.stat_labels[label].config(text=str(val))

        self.completion_label.config(text=f"{s['rate']}%")
        self.ring_canvas.delete("all")
        self.draw_progress_ring(self.ring_canvas, 60, 60, 50, s["rate"],
                                fg=CLR_ON_PRIMARY, bg="#818cf8", width=10)

        today = datetime.now().date().isoformat()

        for quad in self.quadrant_labels:
            self.quadrant_labels[quad].delete(0, tk.END)
        for t in s["tasks"]:
            quad = t.get("quadrant", "Q2: Schedule")
            if quad in self.quadrant_labels:
                status_icon = "✓" if t.get("status") == "Completed" else "○"
                self.quadrant_labels[quad].insert(tk.END, f"  {status_icon} {t.get('title', '')}")

        self.overdue_listbox.delete(0, tk.END)
        for t in s["tasks"]:
            if t.get("status") == "Completed":
                continue
            dd = self.date_part(t.get("due_date", ""))
            if dd < today:
                self.overdue_listbox.insert(
                    tk.END, f"  ⚠ OVERDUE  {t.get('title', '')}  ({dd})")
            elif dd == today:
                self.overdue_listbox.insert(
                    tk.END, f"  ⏰ TODAY    {t.get('title', '')}  ({dd})")
        if not self.overdue_listbox.size():
            self.overdue_listbox.insert(tk.END, "  ✅ No overdue items!")

        self.work_tasks_listbox.delete(0, tk.END)
        self.personal_tasks_listbox.delete(0, tk.END)
        for t in s["tasks"]:
            cat = t.get("category", "Work")
            icon = "✓" if t.get("status") == "Completed" else "○"
            pri  = "🔴 " if t.get("priority") == "High" else ""
            tags = f"  [{', '.join(t.get('tags', []))}]" if t.get("tags") else ""
            line = f"  {pri}{icon} {t.get('title', '')}{tags}"
            if cat in ("Personal", "Health", "Social"):
                self.personal_tasks_listbox.insert(tk.END, line)
            else:
                self.work_tasks_listbox.insert(tk.END, line)

        self._update_streak_badge()
        self._check_achievements()

    def draw_progress_ring(self, canvas, cx, cy, r, pct, fg, bg, width=8):
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=bg, width=width)
        if pct > 0:
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=90, extent=-(360 * pct / 100),
                              outline=fg, width=width, style=tk.ARC)

    def start_quote_rotation(self):
        self.rotate_quote()

    def rotate_quote(self):
        try:
            if hasattr(self, "quote_label") and self.quote_label.winfo_exists():
                self.quote_label.config(
                    text=f"❝ {QUOTES[self.quote_index % len(QUOTES)]} ❞")
                self.quote_index += 1
                self.quote_job = self.root.after(10000, self.rotate_quote)
        except:
            pass

    def _check_achievements(self):
        data = self.load_user_data()
        stats = data.get("user_stats", {})
        achievements = data.get("achievements", [])
        unlocked = stats.get("achievements_unlocked", [])

        achievement_defs = [
            {"id": "first_task", "name": "First Step", "desc": "Complete your first task",
             "condition": lambda d: sum(1 for t in d.get("tasks", []) if t.get("status") == "Completed") >= 1},
            {"id": "task_master", "name": "Task Master", "desc": "Complete 10 tasks",
             "condition": lambda d: sum(1 for t in d.get("tasks", []) if t.get("status") == "Completed") >= 10},
            {"id": "streak_7", "name": "Weekly Warrior", "desc": "Maintain a 7-day streak",
             "condition": lambda d: self._calc_streak() >= 7},
            {"id": "clepsydra_master", "name": "clepsydra Master", "desc": "Complete 10 clepsydra sessions",
             "condition": lambda d: self.clepsydra_count >= 10},
        ]

        new_unlocked = []
        for ach in achievement_defs:
            if ach["id"] not in unlocked and ach["condition"](data):
                new_unlocked.append(ach["id"])
                if ach["id"] not in [a.get("id") for a in achievements]:
                    achievements.append({
                        "id": ach["id"],
                        "name": ach["name"],
                        "description": ach["desc"],
                        "unlocked_at": _now_iso()
                    })
                    stats["xp"] = stats.get("xp", 0) + 50
                    self._show_notification(f"🏆 Achievement Unlocked: {ach['name']}!")

        if new_unlocked:
            stats["achievements_unlocked"] = list(set(unlocked + new_unlocked))
            data["user_stats"] = stats
            data["achievements"] = achievements
            self.save_user_data(data)
            self._update_level()

    def _add_xp(self, amount):
        data = self.load_user_data()
        stats = data.get("user_stats", {})
        stats["xp"] = stats.get("xp", 0) + amount
        stats["points_this_week"] = stats.get("points_this_week", 0) + amount
        data["user_stats"] = stats
        self.save_user_data(data)
        self._update_level()
        if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():
            self.refresh_dashboard()

    def _update_level(self):
        data = self.load_user_data()
        stats = data.get("user_stats", {})
        xp = stats.get("xp", 0)
        level = 1
        while xp >= level * 100:
            xp -= level * 100
            level += 1
        stats["level"] = level
        stats["xp"] = xp
        data["user_stats"] = stats
        self.save_user_data(data)

    def _show_notification(self, message):
        try:
            if hasattr(self, 'quote_label'):
                original = self.quote_label.cget("text")
                self.quote_label.config(text=f"✨ {message} ✨")
                self.root.after(5000, lambda: self.quote_label.config(text=original))
        except:
            pass