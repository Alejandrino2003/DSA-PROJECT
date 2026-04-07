"""
VIAM CENTRIC - Add Item Tab (Event / Task / To-Do forms)
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER_HIGH,
    CLR_PRIMARY, CLR_SUCCESS, CLR_TERTIARY, CLR_WARNING,
    CLR_ON_SURFACE, CLR_OUTLINE_VARIANT, CATEGORY_COLORS,
)
from models import _now_iso


class AddItemMixin:
    """Mixin providing the Add Item tab with Event, Task, and To-Do forms."""

    def build_add_item_tab(self):
        self.add_sub_notebook = ttk.Notebook(self.add_item_tab)
        self.add_sub_notebook.pack(fill="both", expand=True, padx=16, pady=16)

        for title, builder in [
            ("📅 Event", self.build_event_form),
            ("✓ Task",   self.build_task_form),
            ("□ To-Do",  self.build_todo_form),
        ]:
            tab = ttk.Frame(self.add_sub_notebook)
            self.add_sub_notebook.add(tab, text=title)
            builder(tab)

    # ── Event form ────────────────────────────────────────────────────────────

    def build_event_form(self, parent):
        c = tk.Frame(parent, bg=CLR_SURFACE)
        c.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_section_header(c, "Create New Event", "📅", CLR_PRIMARY)
        f = self._form_grid(c)

        self.event_title = self.create_entry(f, width=40)
        self.event_date_entry = self.create_entry(f, width=40)
        self.event_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tf = tk.Frame(f, bg=CLR_SURFACE)
        tk.Label(tf, text="Start:", bg=CLR_SURFACE, fg=CLR_ON_SURFACE).pack(side="left")
        self.event_start = self.create_entry(tf, width=10)
        self.event_start.insert(0, "9:00 AM")
        self.event_start.pack(side="left", padx=(4, 8))
        tk.Label(tf, text="→", bg=CLR_SURFACE, fg=CLR_ON_SURFACE).pack(side="left")
        self.event_end = self.create_entry(tf, width=10)
        self.event_end.insert(0, "10:00 AM")
        self.event_end.pack(side="left", padx=(8, 0))

        self.event_location   = self.create_entry(f, width=40)
        self.event_priority   = ttk.Combobox(f, values=["Low", "Medium", "High"],
                                              state="readonly", width=37)
        self.event_priority.set("Medium")
        self.event_category   = ttk.Combobox(f, values=list(CATEGORY_COLORS),
                                              state="readonly", width=37)
        self.event_category.set("Work")
        self.event_recurrence = ttk.Combobox(f, values=["none", "daily", "weekly", "monthly"],
                                              state="readonly", width=37)
        self.event_recurrence.set("none")
        self.event_tags       = self.create_entry(f, width=40)
        self.event_desc       = tk.Text(f, height=4, width=40,
                                        bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE,
                                        relief=tk.FLAT,
                                        highlightthickness=1,
                                        highlightbackground=CLR_OUTLINE_VARIANT)

        for r, (lbl, w) in enumerate([
            ("Event Title *",       self.event_title),
            ("Date *",              self.event_date_entry),
            ("Time",                tf),
            ("Location",            self.event_location),
            ("Priority",            self.event_priority),
            ("Category",            self.event_category),
            ("Recurrence",          self.event_recurrence),
            ("Tags (comma sep.)",   self.event_tags),
            ("Description",         self.event_desc),
        ]):
            self._frow(f, r, lbl, w)

        bf = tk.Frame(c, bg=CLR_SURFACE)
        bf.pack(fill="x", padx=20, pady=(20, 16))
        self.create_button(bf, "Save Event", self.save_event, primary=True).pack(side="right", padx=6)
        self.create_button(bf, "Clear", self.clear_event_form, primary=False).pack(side="right", padx=6)

    # ── Task form ─────────────────────────────────────────────────────────────

    def build_task_form(self, parent):
        c = tk.Frame(parent, bg=CLR_SURFACE)
        c.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_section_header(c, "Create New Task", "✓", CLR_SUCCESS)
        f = self._form_grid(c)

        self.task_title      = self.create_entry(f, width=40)
        self.task_due_date   = self.create_entry(f, width=40)
        self.task_due_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.task_time       = self.create_entry(f, width=40)
        self.task_time.insert(0, "5:00 PM")
        self.task_priority   = ttk.Combobox(f, values=["Low", "Medium", "High"],
                                             state="readonly", width=37)
        self.task_priority.set("Medium")
        self.task_importance = ttk.Combobox(f, values=["Low", "Medium", "High"],
                                             state="readonly", width=37)
        self.task_importance.set("Medium")
        self.task_urgency    = ttk.Combobox(f, values=["Low", "Medium", "High"],
                                             state="readonly", width=37)
        self.task_urgency.set("Medium")
        self.task_quadrant   = ttk.Combobox(f,
                                             values=["Q1: Do First", "Q2: Schedule",
                                                     "Q3: Delegate", "Q4: Eliminate"],
                                             state="readonly", width=37)
        self.task_quadrant.set("Q2: Schedule")
        self.task_status     = ttk.Combobox(f, values=["Pending", "In Progress", "Completed"],
                                             state="readonly", width=37)
        self.task_status.set("Pending")
        self.task_category   = ttk.Combobox(f, values=list(CATEGORY_COLORS),
                                             state="readonly", width=37)
        self.task_category.set("Work")
        self.task_tags       = self.create_entry(f, width=40)
        self.task_estimated  = self.create_entry(f, width=40)
        self.task_estimated.insert(0, "30")
        self.task_desc       = tk.Text(f, height=4, width=40,
                                       bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE,
                                       relief=tk.FLAT,
                                       highlightthickness=1,
                                       highlightbackground=CLR_OUTLINE_VARIANT)

        def update_quadrant(*args):
            urgency_val    = self.task_urgency.get()
            importance_val = self.task_importance.get()
            urgency    = {"Low": 1, "Medium": 3, "High": 5}.get(urgency_val, 3)
            importance = {"Low": 1, "Medium": 3, "High": 5}.get(importance_val, 3)
            if urgency >= 4 and importance >= 4:
                quad = "Q1: Do First"
            elif urgency < 4 and importance >= 4:
                quad = "Q2: Schedule"
            elif urgency >= 4 and importance < 4:
                quad = "Q3: Delegate"
            else:
                quad = "Q4: Eliminate"
            self.task_quadrant.set(quad)

        self.task_urgency.bind("<<ComboboxSelected>>", update_quadrant)
        self.task_importance.bind("<<ComboboxSelected>>", update_quadrant)

        for r, (lbl, w) in enumerate([
            ("Task Title *",      self.task_title),
            ("Due Date *",        self.task_due_date),
            ("Time",              self.task_time),
            ("Priority",          self.task_priority),
            ("Importance",        self.task_importance),
            ("Urgency",           self.task_urgency),
            ("Quadrant (auto)",   self.task_quadrant),
            ("Status",            self.task_status),
            ("Category",          self.task_category),
            ("Tags (comma sep.)", self.task_tags),
            ("Est. Minutes",      self.task_estimated),
            ("Description",       self.task_desc),
        ]):
            self._frow(f, r, lbl, w)

        bf = tk.Frame(c, bg=CLR_SURFACE)
        bf.pack(fill="x", padx=20, pady=(20, 16))
        self.create_button(bf, "Save Task", self.save_task, primary=True).pack(side="right", padx=6)
        self.create_button(bf, "Clear", self.clear_task_form, primary=False).pack(side="right", padx=6)

    # ── To-Do form ────────────────────────────────────────────────────────────

    def build_todo_form(self, parent):
        c = tk.Frame(parent, bg=CLR_SURFACE)
        c.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_section_header(c, "Create New To-Do", "□", CLR_TERTIARY)
        f = self._form_grid(c)

        self.todo_title    = self.create_entry(f, width=40)
        self.todo_date     = self.create_entry(f, width=40)
        self.todo_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.todo_priority = ttk.Combobox(f, values=["Low", "Medium", "High"],
                                           state="readonly", width=37)
        self.todo_priority.set("Low")
        self.todo_tags     = self.create_entry(f, width=40)
        self.todo_notes    = tk.Text(f, height=4, width=40,
                                     bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE,
                                     relief=tk.FLAT,
                                     highlightthickness=1,
                                     highlightbackground=CLR_OUTLINE_VARIANT)

        for r, (lbl, w) in enumerate([
            ("To-Do Title *",     self.todo_title),
            ("Date *",            self.todo_date),
            ("Priority",          self.todo_priority),
            ("Tags (comma sep.)", self.todo_tags),
            ("Notes",             self.todo_notes),
        ]):
            self._frow(f, r, lbl, w)

        bf = tk.Frame(c, bg=CLR_SURFACE)
        bf.pack(fill="x", padx=20, pady=(20, 16))
        self.create_button(bf, "Save To-Do", self.save_todo, primary=True).pack(side="right", padx=6)
        self.create_button(bf, "Clear", self.clear_todo_form, primary=False).pack(side="right", padx=6)

    # ── Save methods ──────────────────────────────────────────────────────────

    def save_event(self):
        title    = self.event_title.get().strip()
        date_str = self.event_date_entry.get().strip()
        if not title or not date_str:
            messagebox.showerror("Error", "Title and Date required."); return
        try:
            s_dt = datetime.strptime(f"{date_str} {self.event_start.get().strip()}", "%Y-%m-%d %I:%M %p")
            e_dt = datetime.strptime(f"{date_str} {self.event_end.get().strip()}",   "%Y-%m-%d %I:%M %p")
        except Exception as ex:
            messagebox.showerror("Error", f"Time format: 9:00 AM\n{ex}"); return
        if e_dt <= s_dt:
            messagebox.showerror("Error", "End time must be after start time."); return
        raw_tags = [x.strip() for x in self.event_tags.get().split(",") if x.strip()]
        data = self.load_user_data()
        data["events"].append({
            "id":          self.next_id(data["events"]),
            "title":       title,
            "description": self.event_desc.get("1.0", tk.END).strip(),
            "start_time":  s_dt.isoformat(),
            "end_time":    e_dt.isoformat(),
            "location":    self.event_location.get().strip(),
            "priority":    self.event_priority.get(),
            "category":    self.event_category.get(),
            "recurrence":  self.event_recurrence.get(),
            "tags":        raw_tags,
            "created_at":  _now_iso(),
            "updated_at":  _now_iso(),
        })
        self.save_user_data(data)
        self._add_xp(20)
        messagebox.showinfo("Saved", "✅ Event saved!")
        self.clear_event_form()
        self.refresh_dashboard()
        self.refresh_calendar_view()

    def save_task(self):
        title    = self.task_title.get().strip()
        date_str = self.task_due_date.get().strip()
        if not title or not date_str:
            messagebox.showerror("Error", "Title and Due Date required."); return
        try:
            due = datetime.strptime(f"{date_str} {self.task_time.get().strip()}", "%Y-%m-%d %I:%M %p")
        except Exception as ex:
            messagebox.showerror("Error", f"Time format: 5:00 PM\n{ex}"); return
        raw_tags = [x.strip() for x in self.task_tags.get().split(",") if x.strip()]
        try:
            estimated = int(self.task_estimated.get().strip())
        except:
            estimated = 30
        data = self.load_user_data()
        data["tasks"].append({
            "id":               self.next_id(data["tasks"]),
            "title":            title,
            "description":      self.task_desc.get("1.0", tk.END).strip(),
            "due_date":         due.isoformat(),
            "priority":         self.task_priority.get(),
            "importance":       self.task_importance.get(),
            "urgency":          self.task_urgency.get(),
            "quadrant":         self.task_quadrant.get(),
            "status":           self.task_status.get(),
            "category":         self.task_category.get(),
            "tags":             raw_tags,
            "estimated_minutes": estimated,
            "actual_minutes":   0,
            "created_at":       _now_iso(),
            "updated_at":       _now_iso(),
        })
        self.save_user_data(data)
        self._add_xp(15)
        messagebox.showinfo("Saved", "✅ Task saved!")
        self.clear_task_form()
        self.refresh_dashboard()

    def save_todo(self):
        title    = self.todo_title.get().strip()
        date_str = self.todo_date.get().strip()
        if not title or not date_str:
            messagebox.showerror("Error", "Title and Date required."); return
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Date must be YYYY-MM-DD"); return
        raw_tags = [x.strip() for x in self.todo_tags.get().split(",") if x.strip()]
        data  = self.load_user_data()
        todos = data["daily_todos"].setdefault(date_str, [])
        todos.append({
            "id":         self.next_id(todos),
            "title":      title,
            "notes":      self.todo_notes.get("1.0", tk.END).strip(),
            "priority":   self.todo_priority.get(),
            "done":       False,
            "tags":       raw_tags,
            "created_at": _now_iso(),
        })
        self.save_user_data(data)
        self._add_xp(10)
        messagebox.showinfo("Saved", "✅ To-Do saved!")
        self.clear_todo_form()
        self.refresh_dashboard()
        self.refresh_calendar_view()

    # ── Clear forms ───────────────────────────────────────────────────────────

    def clear_event_form(self):
        self.event_title.delete(0, tk.END)
        self.event_location.delete(0, tk.END)
        self.event_tags.delete(0, tk.END)
        self.event_desc.delete("1.0", tk.END)
        self.event_priority.set("Medium")
        self.event_category.set("Work")
        self.event_recurrence.set("none")
        self.event_date_entry.delete(0, tk.END)
        self.event_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.event_start.delete(0, tk.END); self.event_start.insert(0, "9:00 AM")
        self.event_end.delete(0, tk.END);   self.event_end.insert(0, "10:00 AM")

    def clear_task_form(self):
        self.task_title.delete(0, tk.END)
        self.task_tags.delete(0, tk.END)
        self.task_desc.delete("1.0", tk.END)
        self.task_priority.set("Medium")
        self.task_status.set("Pending")
        self.task_category.set("Work")
        self.task_importance.set("Medium")
        self.task_urgency.set("Medium")
        self.task_quadrant.set("Q2: Schedule")
        self.task_estimated.delete(0, tk.END)
        self.task_estimated.insert(0, "30")
        self.task_due_date.delete(0, tk.END)
        self.task_due_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.task_time.delete(0, tk.END)
        self.task_time.insert(0, "5:00 PM")

    def clear_todo_form(self):
        self.todo_title.delete(0, tk.END)
        self.todo_tags.delete(0, tk.END)
        self.todo_notes.delete("1.0", tk.END)
        self.todo_priority.set("Low")
        self.todo_date.delete(0, tk.END)
        self.todo_date.insert(0, datetime.now().strftime("%Y-%m-%d"))