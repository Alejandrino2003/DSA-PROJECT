"""
VIAM CENTRIC - Calendar Tab
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER, CLR_SURFACE_CONTAINER_HIGH,
    CLR_PRIMARY, CLR_PRIMARY_FIXED, CLR_ON_PRIMARY,
    CLR_SECONDARY_CONTAINER, CLR_TERTIARY_CONTAINER,
    CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT,
    CLR_ERROR, CLR_ERROR_CONTAINER, CLR_SUCCESS, CLR_WARNING,
    CLR_OUTLINE_VARIANT, CATEGORY_COLORS,
)
from models import _now_iso

try:
    import tkcalendar as tkc
    TKCAL_AVAILABLE = True
except ImportError:
    TKCAL_AVAILABLE = False


class CalendarMixin:
    """Mixin providing Calendar tab, agenda view, and edit dialogs."""

    def build_calendar(self):
        main_frame = tk.Frame(self.calendar_tab, bg=CLR_SURFACE)
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        left_panel = self.create_card(main_frame, bg=CLR_SURFACE, border=True)
        left_panel.pack(side="left", fill="both", expand=True, padx=6)

        if TKCAL_AVAILABLE:
            self.calendar_widget = tkc.Calendar(
                left_panel, selectmode="day", date_pattern="yyyy-mm-dd",
                font=("Segoe UI", 10),
                background=CLR_SURFACE, foreground=CLR_ON_SURFACE,
                selectbackground=CLR_PRIMARY, selectforeground=CLR_ON_PRIMARY,
                normalbackground=CLR_SURFACE_CONTAINER,
                weekendbackground=CLR_SURFACE_CONTAINER_HIGH)
            self.calendar_widget.pack(padx=16, pady=16, fill="both", expand=True)
            self.calendar_widget.bind("<<CalendarSelected>>", self.on_calendar_select)
            self.bind_calendar_context_menu()
            self.calendar_widget.bind("<<CalendarMonthChanged>>",
                                       lambda e: self.bind_calendar_context_menu())
        else:
            tk.Label(left_panel,
                     text="Install tkcalendar:\npip install tkcalendar",
                     font=("Segoe UI", 12),
                     bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT,
                     justify="center").pack(expand=True)
            self.calendar_widget = None

        right_panel = self.create_card(main_frame, bg=CLR_SURFACE, border=True)
        right_panel.pack(side="left", fill="both", expand=True, padx=6)

        self.agenda_header = tk.Label(right_panel, text="",
                                       font=("Segoe UI", 14, "bold"),
                                       bg=CLR_SURFACE, fg=CLR_PRIMARY)
        self.agenda_header.pack(anchor="w", padx=16, pady=(16, 8))

        self.agenda_listbox = tk.Listbox(right_panel, height=20,
                                          font=("Segoe UI", 10),
                                          bg=CLR_SURFACE_CONTAINER,
                                          fg=CLR_ON_SURFACE,
                                          selectbackground=CLR_PRIMARY_FIXED,
                                          relief=tk.FLAT)
        self.agenda_listbox.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        quick_bar = tk.Frame(right_panel, bg=CLR_SURFACE)
        quick_bar.pack(fill="x", padx=16, pady=(0, 12))
        self.create_button(quick_bar, "+ Add Event here",
                           self.quick_add_event,
                           primary=True).pack(side="left", padx=(0, 6))
        self.create_button(quick_bar, "+ Add Task here",
                           lambda: self.quick_add_for_date(self.selected_date, "task"),
                           primary=False).pack(side="left", padx=(0, 6))
        self.create_button(quick_bar, "+ Add To-Do here",
                           lambda: self.quick_add_for_date(self.selected_date, "todo"),
                           primary=False).pack(side="left")

        self.refresh_calendar_view()

    # ── Context menu ──────────────────────────────────────────────────────────

    def bind_calendar_context_menu(self):
        if not self.calendar_widget:
            return
        def _bind(w):
            w.bind("<Button-3>", self.show_calendar_context_menu, add="+")
            for c in w.winfo_children():
                _bind(c)
        _bind(self.calendar_widget)

    def show_calendar_context_menu(self, event):
        if not self.calendar_widget:
            return
        try:
            date_str = self.calendar_widget.get_date()
        except:
            return
        data  = self.load_user_data()
        evs   = [e for e in data.get("events", [])
                 if self.date_part(e.get("start_time", "")) == date_str]
        tasks = [t for t in data.get("tasks", [])
                 if self.date_part(t.get("due_date", "")) == date_str]
        todos = data.get("daily_todos", {}).get(date_str, [])
        has   = bool(evs or tasks or todos)

        m = tk.Menu(self.root, tearoff=0,
                    bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE,
                    activebackground=CLR_PRIMARY, activeforeground=CLR_ON_PRIMARY)
        m.add_command(label=f"📅 {date_str}", state="disabled",
                      font=("Segoe UI", 10, "bold"))
        m.add_separator()

        del_menu  = tk.Menu(m, tearoff=0, bg=CLR_SURFACE_CONTAINER,
                            fg=CLR_ON_SURFACE,
                            activebackground=CLR_ERROR,
                            activeforeground=CLR_ON_PRIMARY)
        edit_menu = tk.Menu(m, tearoff=0, bg=CLR_SURFACE_CONTAINER,
                            fg=CLR_ON_SURFACE,
                            activebackground=CLR_PRIMARY,
                            activeforeground=CLR_ON_PRIMARY)

        for ev in evs:
            t = ev.get("title", "")[:35]
            del_menu.add_command(label=f"🗑 Event: {t}",
                                 command=lambda e=ev: self.delete_item("event", e, date_str))
            edit_menu.add_command(label=f"✏ Event: {t}",
                                  command=lambda e=ev: self.edit_event_dialog(e, date_str))
        for tk_ in tasks:
            t = tk_.get("title", "")[:35]
            del_menu.add_command(label=f"🗑 Task: {t}",
                                 command=lambda x=tk_: self.delete_item("task", x, date_str))
            edit_menu.add_command(label=f"✏ Task: {t}",
                                  command=lambda x=tk_: self.edit_task_dialog(x, date_str))
        for td in todos:
            t = td.get("title", "")[:35]
            del_menu.add_command(label=f"🗑 To-Do: {t}",
                                 command=lambda x=td, d=date_str: self.delete_item("todo", x, d))
            edit_menu.add_command(label=f"✏ To-Do: {t}",
                                  command=lambda x=td, d=date_str: self.edit_todo_dialog(x, d))

        m.add_cascade(label="🗑 Delete", menu=del_menu,
                      state="normal" if has else "disabled")
        m.add_cascade(label="✏ Edit",   menu=edit_menu,
                      state="normal" if has else "disabled")
        m.tk_popup(event.x_root, event.y_root)

    def delete_item(self, kind, item, date_str):
        if not messagebox.askyesno("Confirm Delete",
                f"Delete '{item.get('title', 'this item')}'?\nCannot be undone."):
            return
        data = self.load_user_data()
        if kind == "event":
            data["events"] = [e for e in data["events"]
                              if e.get("id") != item.get("id")]
        elif kind == "task":
            data["tasks"] = [t for t in data["tasks"]
                             if t.get("id") != item.get("id")]
        else:
            todos = data["daily_todos"].get(date_str, [])
            data["daily_todos"][date_str] = [
                t for t in todos if t.get("id") != item.get("id")]
            if not data["daily_todos"][date_str]:
                del data["daily_todos"][date_str]
        self.save_user_data(data)
        self.refresh_calendar_view()
        self.refresh_dashboard()

    # ── Edit dialogs ──────────────────────────────────────────────────────────

    def edit_event_dialog(self, ev, date_str):
        dlg, form = self._dlg("Edit Event", 680, CLR_PRIMARY)
        try:
            st_s = datetime.fromisoformat(ev["start_time"]).strftime("%I:%M %p").lstrip("0")
            en_s = datetime.fromisoformat(ev["end_time"]).strftime("%I:%M %p").lstrip("0")
        except:
            st_s, en_s = "9:00 AM", "10:00 AM"

        title_e  = self.create_entry(form, width=38); title_e.insert(0, ev.get("title", ""))
        date_e   = self.create_entry(form, width=38); date_e.insert(0, date_str)
        start_e  = self.create_entry(form, width=18); start_e.insert(0, st_s)
        end_e    = self.create_entry(form, width=18); end_e.insert(0, en_s)
        loc_e    = self.create_entry(form, width=38); loc_e.insert(0, ev.get("location", ""))
        pri_cb   = ttk.Combobox(form, values=["Low", "Medium", "High"], state="readonly", width=36)
        pri_cb.set(ev.get("priority", "Medium"))
        cat_cb   = ttk.Combobox(form, values=list(CATEGORY_COLORS), state="readonly", width=36)
        cat_cb.set(ev.get("category", "Work"))
        rec_cb   = ttk.Combobox(form, values=["none", "daily", "weekly", "monthly"],
                                state="readonly", width=36)
        rec_cb.set(ev.get("recurrence", "none"))
        tags_e   = self.create_entry(form, width=38)
        tags_e.insert(0, ", ".join(ev.get("tags", [])))
        desc_t   = tk.Text(form, height=4, width=38,
                           bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE,
                           relief=tk.FLAT,
                           highlightthickness=1, highlightbackground=CLR_OUTLINE_VARIANT)
        desc_t.insert("1.0", ev.get("description", ""))

        tf = tk.Frame(form, bg=CLR_SURFACE)
        tk.Label(tf, text="Start:", bg=CLR_SURFACE).pack(side="left")
        start_e.pack(side="left", padx=(4, 12))
        tk.Label(tf, text="→", bg=CLR_SURFACE).pack(side="left")
        end_e.pack(side="left", padx=(12, 0))

        for r, (lbl, w) in enumerate([
            ("Title *",      title_e),
            ("Date *",       date_e),
            ("Time",         tf),
            ("Location",     loc_e),
            ("Priority",     pri_cb),
            ("Category",     cat_cb),
            ("Recurrence",   rec_cb),
            ("Tags",         tags_e),
            ("Description",  desc_t),
        ]):
            self._dlg_row(form, r, lbl, w)

        def save():
            ds, ts = date_e.get().strip(), title_e.get().strip()
            if not ts or not ds:
                messagebox.showerror("Error", "Title and Date required.", parent=dlg); return
            try:
                s_dt = datetime.strptime(f"{ds} {start_e.get().strip()}", "%Y-%m-%d %I:%M %p")
                e_dt = datetime.strptime(f"{ds} {end_e.get().strip()}", "%Y-%m-%d %I:%M %p")
            except:
                messagebox.showerror("Error", "Time format: 9:00 AM", parent=dlg); return
            if e_dt <= s_dt:
                messagebox.showerror("Error", "End must be after start.", parent=dlg); return
            raw_tags = [x.strip() for x in tags_e.get().split(",") if x.strip()]
            data = self.load_user_data()
            for e in data["events"]:
                if e.get("id") == ev.get("id"):
                    e.update(title=ts, start_time=s_dt.isoformat(),
                             end_time=e_dt.isoformat(),
                             location=loc_e.get().strip(),
                             priority=pri_cb.get(), category=cat_cb.get(),
                             recurrence=rec_cb.get(), tags=raw_tags,
                             description=desc_t.get("1.0", tk.END).strip(),
                             updated_at=_now_iso()); break
            self.save_user_data(data)
            self.refresh_calendar_view(); self.refresh_dashboard(); dlg.destroy()

        bf = tk.Frame(dlg, bg=CLR_SURFACE); bf.pack(fill="x", padx=20, pady=(0, 16))
        self.create_button(bf, "Save Changes", save, primary=True).pack(side="right", padx=6)
        self.create_button(bf, "Cancel", dlg.destroy, primary=False).pack(side="right", padx=6)

    def edit_task_dialog(self, task, date_str):
        dlg, form = self._dlg("Edit Task", 640, CLR_SUCCESS)
        try:
            tm_s = datetime.fromisoformat(task["due_date"]).strftime("%I:%M %p").lstrip("0")
        except:
            tm_s = "5:00 PM"

        title_e = self.create_entry(form, width=38); title_e.insert(0, task.get("title", ""))
        date_e  = self.create_entry(form, width=38); date_e.insert(0, date_str)
        time_e  = self.create_entry(form, width=38); time_e.insert(0, tm_s)
        pri_cb  = ttk.Combobox(form, values=["Low", "Medium", "High"], state="readonly", width=36)
        pri_cb.set(task.get("priority", "Medium"))
        sts_cb  = ttk.Combobox(form, values=["Pending", "In Progress", "Completed"],
                               state="readonly", width=36)
        sts_cb.set(task.get("status", "Pending"))
        cat_cb  = ttk.Combobox(form, values=list(CATEGORY_COLORS), state="readonly", width=36)
        cat_cb.set(task.get("category", "Work"))
        tags_e  = self.create_entry(form, width=38)
        tags_e.insert(0, ", ".join(task.get("tags", [])))
        desc_t  = tk.Text(form, height=4, width=38,
                          bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE,
                          relief=tk.FLAT,
                          highlightthickness=1, highlightbackground=CLR_OUTLINE_VARIANT)
        desc_t.insert("1.0", task.get("description", ""))

        for r, (lbl, w) in enumerate([
            ("Title *",     title_e),
            ("Due Date *",  date_e),
            ("Time",        time_e),
            ("Priority",    pri_cb),
            ("Status",      sts_cb),
            ("Category",    cat_cb),
            ("Tags",        tags_e),
            ("Description", desc_t),
        ]):
            self._dlg_row(form, r, lbl, w)

        def save():
            ts, ds = title_e.get().strip(), date_e.get().strip()
            if not ts or not ds:
                messagebox.showerror("Error", "Title and Date required.", parent=dlg); return
            try:
                due = datetime.strptime(f"{ds} {time_e.get().strip()}", "%Y-%m-%d %I:%M %p")
            except:
                messagebox.showerror("Error", "Time format: 5:00 PM", parent=dlg); return
            raw_tags = [x.strip() for x in tags_e.get().split(",") if x.strip()]
            data = self.load_user_data()
            for t in data["tasks"]:
                if t.get("id") == task.get("id"):
                    t.update(title=ts, due_date=due.isoformat(),
                             priority=pri_cb.get(), status=sts_cb.get(),
                             category=cat_cb.get(), tags=raw_tags,
                             description=desc_t.get("1.0", tk.END).strip(),
                             updated_at=_now_iso()); break
            self.save_user_data(data)
            self.refresh_calendar_view(); self.refresh_dashboard(); dlg.destroy()

        bf = tk.Frame(dlg, bg=CLR_SURFACE); bf.pack(fill="x", padx=20, pady=(0, 16))
        self.create_button(bf, "Save Changes", save, primary=True).pack(side="right", padx=6)
        self.create_button(bf, "Cancel", dlg.destroy, primary=False).pack(side="right", padx=6)

    def edit_todo_dialog(self, todo, date_str):
        dlg, form = self._dlg("Edit To-Do", 500, CLR_WARNING)
        title_e = self.create_entry(form, width=38); title_e.insert(0, todo.get("title", ""))
        pri_cb  = ttk.Combobox(form, values=["Low", "Medium", "High"], state="readonly", width=36)
        pri_cb.set(todo.get("priority", "Low"))
        done_v  = tk.BooleanVar(value=todo.get("done", False))
        done_cb = tk.Checkbutton(form, text="Mark as Done", variable=done_v,
                                  bg=CLR_SURFACE, fg=CLR_ON_SURFACE,
                                  selectcolor=CLR_PRIMARY_FIXED, font=("Segoe UI", 10))
        tags_e  = self.create_entry(form, width=38)
        tags_e.insert(0, ", ".join(todo.get("tags", [])))
        notes_t = tk.Text(form, height=5, width=38,
                          bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_ON_SURFACE,
                          relief=tk.FLAT,
                          highlightthickness=1, highlightbackground=CLR_OUTLINE_VARIANT)
        notes_t.insert("1.0", todo.get("notes", ""))

        for r, (lbl, w) in enumerate([
            ("Title *",  title_e),
            ("Priority", pri_cb),
            ("Done",     done_cb),
            ("Tags",     tags_e),
            ("Notes",    notes_t),
        ]):
            self._dlg_row(form, r, lbl, w)

        def save():
            ts = title_e.get().strip()
            if not ts:
                messagebox.showerror("Error", "Title required.", parent=dlg); return
            raw_tags = [x.strip() for x in tags_e.get().split(",") if x.strip()]
            data  = self.load_user_data()
            todos = data["daily_todos"].get(date_str, [])
            for i, t in enumerate(todos):
                if t.get("id") == todo.get("id"):
                    todos[i].update(title=ts, priority=pri_cb.get(),
                                    done=done_v.get(), tags=raw_tags,
                                    notes=notes_t.get("1.0", tk.END).strip())
                    break
            self.save_user_data(data)
            self.refresh_calendar_view(); self.refresh_dashboard(); dlg.destroy()

        bf = tk.Frame(dlg, bg=CLR_SURFACE); bf.pack(fill="x", padx=20, pady=(0, 16))
        self.create_button(bf, "Save Changes", save, primary=True).pack(side="right", padx=6)
        self.create_button(bf, "Cancel", dlg.destroy, primary=False).pack(side="right", padx=6)

    # ── Quick add / view ──────────────────────────────────────────────────────

    def quick_add_for_date(self, date_str, kind):
        self.switch_tab(2)
        tab_map = {"event": 0, "task": 1, "todo": 2}
        try:
            self.add_sub_notebook.select(tab_map.get(kind, 0))
        except:
            pass
        if kind == "event" and hasattr(self, "event_date_entry"):
            self.event_date_entry.delete(0, tk.END)
            self.event_date_entry.insert(0, date_str)
        elif kind == "task" and hasattr(self, "task_due_date"):
            self.task_due_date.delete(0, tk.END)
            self.task_due_date.insert(0, date_str)
        elif kind == "todo" and hasattr(self, "todo_date"):
            self.todo_date.delete(0, tk.END)
            self.todo_date.insert(0, date_str)

    def refresh_calendar_view(self):
        date_str = (self.calendar_widget.get_date()
                    if self.calendar_widget else self.selected_date)
        self.update_agenda(date_str)
        if not self.calendar_widget:
            return
        try:
            self.calendar_widget.calevent_remove("all")
            data = self.load_user_data()
            self.calendar_widget.tag_config("event",  background=CLR_PRIMARY_FIXED)
            self.calendar_widget.tag_config("task",   background=CLR_SECONDARY_CONTAINER)
            self.calendar_widget.tag_config("todo",   background=CLR_TERTIARY_CONTAINER)
            self.calendar_widget.tag_config("overdue", background=CLR_ERROR_CONTAINER)
            today = datetime.now().date().isoformat()
            ev_dates   = {e.get("start_time", "")[:10] for e in data["events"]}
            task_dates = {t.get("due_date", "")[:10]   for t in data["tasks"]}
            todo_dates = set(data["daily_todos"])
            overdue_dt = {t.get("due_date", "")[:10] for t in data["tasks"]
                          if t.get("status") != "Completed"
                          and self.date_part(t.get("due_date", "")) < today}
            for d in ev_dates | task_dates | todo_dates:
                try:
                    obj = datetime.strptime(d, "%Y-%m-%d").date()
                    tag = ("overdue" if d in overdue_dt
                           else "event"  if d in ev_dates
                           else "task"   if d in task_dates
                           else "todo")
                    self.calendar_widget.calevent_create(obj, "●", tag)
                except:
                    pass
        except Exception as e:
            print(f"Calendar refresh error: {e}")

    def on_calendar_select(self, event):
        if self.calendar_widget:
            self.selected_date = self.calendar_widget.get_date()
            self.update_agenda(self.selected_date)

    def update_agenda(self, date_str):
        try:
            self.agenda_header.config(
                text=datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d, %Y"))
        except:
            self.agenda_header.config(text=date_str)
        self.agenda_listbox.delete(0, tk.END)
        data   = self.load_user_data()
        events = [e for e in data["events"]
                  if e.get("start_time", "")[:10] == date_str]
        tasks  = [t for t in data["tasks"]
                  if t.get("due_date", "")[:10] == date_str]
        todos  = data["daily_todos"].get(date_str, [])
        if events:
            self.agenda_listbox.insert(tk.END, "── EVENTS ──────────────────")
            for e in sorted(events, key=lambda x: x.get("start_time", "")):
                try:
                    ts = datetime.fromisoformat(e["start_time"]).strftime("%I:%M %p").lstrip("0")
                except:
                    ts = ""
                pi  = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(e.get("priority", ""), "⚪")
                cat = f"  [{e.get('category', '')}]" if e.get("category") else ""
                rec = f"  ↻{e.get('recurrence')}" if e.get("recurrence", "none") != "none" else ""
                tgs = f"  #{' #'.join(e.get('tags', []))}" if e.get("tags") else ""
                self.agenda_listbox.insert(tk.END,
                    f"  {pi} {ts} — {e.get('title', '')}{cat}{rec}{tgs}")
            self.agenda_listbox.insert(tk.END, "")
        if tasks:
            self.agenda_listbox.insert(tk.END, "── TASKS ────────────────────")
            for t in tasks:
                si  = "✅" if t.get("status") == "Completed" else "⏳"
                tgs = f"  #{' #'.join(t.get('tags', []))}" if t.get("tags") else ""
                self.agenda_listbox.insert(tk.END,
                    f"  {si} {t.get('title', '')}  [{t.get('status', 'Pending')}]{tgs}")
            self.agenda_listbox.insert(tk.END, "")
        if todos:
            self.agenda_listbox.insert(tk.END, "── TO-DOS ───────────────────")
            for td in todos:
                di  = "✅" if td.get("done") else "⬜"
                tgs = f"  #{' #'.join(td.get('tags', []))}" if td.get("tags") else ""
                self.agenda_listbox.insert(tk.END,
                    f"  {di} {td.get('title', '')}{tgs}")
            self.agenda_listbox.insert(tk.END, "")
        if not (events or tasks or todos):
            self.agenda_listbox.insert(tk.END, "  No items scheduled for this day.")
            self.agenda_listbox.insert(tk.END, "  Right-click the calendar to add items.")

    def quick_add_event(self):
        self.quick_add_for_date(self.selected_date, "event")