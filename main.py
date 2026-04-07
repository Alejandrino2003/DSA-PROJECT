"""
VIAM CENTRIC - Personal Scheduler
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER, CLR_SURFACE_CONTAINER_HIGH,
    CLR_PRIMARY, CLR_PRIMARY_FIXED, CLR_ON_PRIMARY,
    CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT,
    CLR_OUTLINE_VARIANT, CLR_WARNING,
    NAV_ITEMS, USERS_FILENAME, DATA_FOLDER, SETTINGS_FILENAME,
)

# ── Mixin imports (separated modules) ────────────────────────────────────────
from UI                     import UIMixin
from authentication         import AuthMixin
from data                   import DataMixin
from Timer                  import TimerMixin
from DashboardTab           import DashboardMixin
from CalendarTab            import CalendarMixin
from AddItemTab             import AddItemMixin
from NoteTab                import NotesMixin
from AnalyticsTab           import AnalyticsMixin
from HabitsTab              import HabitsMixin

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import tkcalendar as tkc
    TKCAL_AVAILABLE = True
except ImportError:
    TKCAL_AVAILABLE = False


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class PersonalScheduler(
    UIMixin,
    AuthMixin,
    DataMixin,
    TimerMixin,
    DashboardMixin,
    CalendarMixin,
    AddItemMixin,
    NotesMixin,
    AnalyticsMixin,
    HabitsMixin,
):
    """
    Main application class. All feature logic lives in the mixin modules.
    This class only handles:
      - Initialization & window setup
      - Main layout / sidebar
      - Clock, streak, search, and tab-switching
    """

    def __init__(self, root):
        self.root = root
        self.root.title("VIAM CENTRIC – Personal Scheduler v3.1")
        self.root.geometry("1400x850")
        self.root.minsize(1100, 700)
        self.root.configure(bg=CLR_SURFACE)

        self.folder        = Path(__file__).resolve().parent
        self.users_file    = self.folder / USERS_FILENAME
        self.data_dir      = self.folder / DATA_FOLDER
        self.data_dir.mkdir(exist_ok=True)
        self.settings_path = self.folder / SETTINGS_FILENAME

        self.current_user: Optional[Dict] = None
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        self.clock_job     = None
        self.quote_job     = None
        self.quote_index   = 0
        self.notebook      = None
        self.calendar_widget = None

        # Timer state
        self.clepsydra_running      = False
        self.clepsydra_remaining    = 0
        self.clepsydra_duration     = 25 * 60
        self.short_break_duration   = 5 * 60
        self.long_break_duration    = 15 * 60
        self.clepsydra_count        = 0
        self.current_timer_mode     = "clepsydra"
        self.clepsydra_auto_break   = True
        self.timer_update_job       = None

        self.setup_styles()
        self.show_login()

    # ── Clock & streak ────────────────────────────────────────────────────────

    def update_clock(self):
        try:
            if not self.clock_label.winfo_exists():
                return
        except:
            return
        self.clock_label.config(text=datetime.now().strftime("%a %b %d • %I:%M %p"))
        self.clock_job = self.root.after(1000, self.update_clock)

    def _calc_streak(self) -> int:
        data = self.load_user_data()
        streak, day = 0, datetime.now().date()
        for _ in range(365):
            if any(t.get("done") for t in
                   data["daily_todos"].get(day.isoformat(), [])):
                streak += 1
                day -= timedelta(days=1)
            else:
                break
        return streak

    def _update_streak_badge(self):
        try:
            if not self.streak_label.winfo_exists():
                return
        except:
            return
        s = self._calc_streak()
        if s > 0:
            self.streak_label.config(text=f"🔥 {s}-day streak!")
        else:
            self.streak_label.config(text="")

    # ── Tab navigation ────────────────────────────────────────────────────────

    def switch_tab(self, index):
        self.notebook.select(index)
        self.update_nav_highlight(index)
        if index == 4:
            self.refresh_analytics()
        elif index == 5:
            self.refresh_habits_view()

    def on_tab_change(self, event):
        index = self.notebook.index(self.notebook.select())
        self.update_nav_highlight(index)
        if index == 1:
            self.refresh_calendar_view()
        elif index == 4:
            self.refresh_analytics()
        elif index == 5:
            self.refresh_habits_view()

    def update_nav_highlight(self, active):
        for idx, btn in self.nav_buttons.items():
            if idx == active:
                btn.configure(bg=CLR_PRIMARY_FIXED, fg=CLR_PRIMARY,
                              font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT,
                              font=("Segoe UI", 10))

    # ── Search ────────────────────────────────────────────────────────────────

    def _on_search(self, *_):
        q = self.search_var.get().strip().lower()
        if not q:
            self.search_results_frame.pack_forget()
            return
        data = self.load_user_data()
        results = []
        for ev in data["events"]:
            if q in ev.get("title", "").lower():
                results.append(f"📅 {ev['title']}  ({self.date_part(ev.get('start_time', ''))})")
        for t in data["tasks"]:
            if q in t.get("title", "").lower():
                results.append(f"✓ {t['title']}  [{t.get('status', '')}]")
        for day, todos in data["daily_todos"].items():
            for td in todos:
                if q in td.get("title", "").lower():
                    done = "✅" if td.get("done") else "⬜"
                    results.append(f"{done} {td['title']}  ({day})")
        self.search_results_list.delete(0, tk.END)
        if results:
            for r in results[:10]:
                self.search_results_list.insert(tk.END, r)
            self.search_results_frame.pack(fill="x", padx=12, pady=(0, 4))
        else:
            self.search_results_list.insert(tk.END, "  No results found")
            self.search_results_frame.pack(fill="x", padx=12, pady=(0, 4))

    # ── Main layout ───────────────────────────────────────────────────────────

    def show_main(self):
        self.clear_window()
        self.root.configure(bg=CLR_SURFACE)

        # Sidebar
        sidebar = tk.Frame(self.root, bg=CLR_SURFACE, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=CLR_SURFACE)
        brand.pack(fill="x", padx=20, pady=(24, 16))
        logo = tk.Frame(brand, bg=CLR_PRIMARY, width=40, height=40)
        logo.pack(side="left")
        logo.pack_propagate(False)
        tk.Label(logo, text="V", font=("Segoe UI", 20, "bold"),
                 bg=CLR_PRIMARY, fg=CLR_ON_PRIMARY).pack(expand=True)
        tk.Label(brand, text="VIAM CENTRIC",
                 font=("Segoe UI", 16, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE).pack(side="left", padx=12)

        user_card = self.create_card(sidebar, bg=CLR_SURFACE_CONTAINER, border=True)
        user_card.pack(fill="x", padx=16, pady=(16, 4))
        tk.Label(user_card,
                 text=f"👤 {self.current_user['username']}",
                 font=("Segoe UI", 11, "bold"),
                 bg=CLR_SURFACE_CONTAINER,
                 fg=CLR_ON_SURFACE).pack(anchor="w", padx=12, pady=(12, 4))

        data = self.load_user_data()
        level = data.get("user_stats", {}).get("level", 1)
        xp    = data.get("user_stats", {}).get("xp", 0)
        next_level_xp = level * 100
        tk.Label(user_card,
                 text=f"⭐ Level {level} ({xp}/{next_level_xp} XP)",
                 font=("Segoe UI", 9),
                 bg=CLR_SURFACE_CONTAINER,
                 fg=CLR_PRIMARY).pack(anchor="w", padx=12, pady=(0, 4))

        self.clock_label = tk.Label(user_card, text="",
                                     font=("Segoe UI", 9),
                                     bg=CLR_SURFACE_CONTAINER,
                                     fg=CLR_ON_SURFACE_VARIANT)
        self.clock_label.pack(anchor="w", padx=12, pady=(0, 4))

        self.streak_label = tk.Label(user_card, text="",
                                      font=("Segoe UI", 9, "bold"),
                                      bg=CLR_SURFACE_CONTAINER,
                                      fg=CLR_WARNING)
        self.streak_label.pack(anchor="w", padx=12, pady=(0, 12))
        self._update_streak_badge()
        self.update_clock()

        ttk.Separator(sidebar).pack(fill="x", padx=16, pady=8)

        # Search bar
        search_frame = tk.Frame(sidebar, bg=CLR_SURFACE)
        search_frame.pack(fill="x", padx=12, pady=(4, 8))
        tk.Label(search_frame, text="🔍",
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT,
                 font=("Segoe UI", 10)).pack(side="left", padx=(4, 0))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                font=("Segoe UI", 9),
                                bg=CLR_SURFACE_CONTAINER_HIGH,
                                fg=CLR_ON_SURFACE,
                                insertbackground=CLR_PRIMARY,
                                relief=tk.FLAT,
                                highlightthickness=1,
                                highlightbackground=CLR_OUTLINE_VARIANT,
                                highlightcolor=CLR_PRIMARY)
        search_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.search_var.trace_add("write", self._on_search)

        self.search_results_frame = tk.Frame(sidebar,
                                              bg=CLR_SURFACE_CONTAINER,
                                              highlightthickness=1,
                                              highlightbackground=CLR_OUTLINE_VARIANT)
        self.search_results_list = tk.Listbox(self.search_results_frame,
                                               font=("Segoe UI", 9),
                                               bg=CLR_SURFACE_CONTAINER,
                                               fg=CLR_ON_SURFACE,
                                               selectbackground=CLR_PRIMARY_FIXED,
                                               relief=tk.FLAT,
                                               highlightthickness=0,
                                               height=6)
        self.search_results_list.pack(fill="both", expand=True, padx=4, pady=4)

        ttk.Separator(sidebar).pack(fill="x", padx=16, pady=4)

        # Nav buttons
        self.nav_buttons = {}
        for icon, label, idx in NAV_ITEMS:
            btn = tk.Button(sidebar,
                            text=f"  {icon}   {label}",
                            font=("Segoe UI", 10),
                            bg=CLR_SURFACE,
                            fg=CLR_ON_SURFACE_VARIANT,
                            relief=tk.FLAT,
                            cursor="hand2",
                            anchor="w", pady=10, padx=20,
                            activebackground=CLR_PRIMARY_FIXED,
                            activeforeground=CLR_PRIMARY,
                            command=lambda i=idx: self.switch_tab(i))
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[idx] = btn

        # Sign Out
        ttk.Separator(sidebar).pack(fill="x", padx=16, pady=8)
        logout_frame = tk.Frame(sidebar, bg=CLR_SURFACE)
        logout_frame.pack(side="bottom", fill="x", padx=16, pady=20)
        self.create_button(logout_frame, "🚪 Sign Out",
                           self.logout, primary=False).pack(fill="x")

        # Main content area
        main_area = tk.Frame(self.root, bg=CLR_SURFACE)
        main_area.pack(side="left", fill="both", expand=True)

        self.notebook = ttk.Notebook(main_area, style="Hidden.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        self.dashboard_tab = ttk.Frame(self.notebook)
        self.calendar_tab  = ttk.Frame(self.notebook)
        self.add_item_tab  = ttk.Frame(self.notebook)
        self.notes_tab     = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)
        self.habits_tab    = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.calendar_tab,  text="Calendar")
        self.notebook.add(self.add_item_tab,  text="Add Item")
        self.notebook.add(self.notes_tab,     text="Notes")
        self.notebook.add(self.analytics_tab, text="Analytics")
        self.notebook.add(self.habits_tab,    text="Habits")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.build_dashboard()
        self.build_calendar()
        self.build_add_item_tab()
        self.build_notes_tab()
        self.build_analytics_tab()
        self.build_habits_tab()

        self.update_nav_highlight(0)
        self.start_quote_rotation()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app  = PersonalScheduler(root)
    root.mainloop()