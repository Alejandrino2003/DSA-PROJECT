"""
VIAM CENTRIC - Habits Tab
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER,
    CLR_PRIMARY, CLR_PRIMARY_FIXED, CLR_SECONDARY,
    CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT,
    CLR_OUTLINE_VARIANT,
)
from models import _now_iso


class HabitsMixin:
    """Mixin providing the Habits tab."""

    def build_habits_tab(self):
        container = tk.Frame(self.habits_tab, bg=CLR_SURFACE)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_section_header(container, "Habit Tracker", "🔄", CLR_SECONDARY)

        # Add habit form
        form_frame = self.create_card(container, bg=CLR_SURFACE_CONTAINER, border=True)
        form_frame.pack(fill="x", padx=20, pady=(0, 16))

        form_inner = tk.Frame(form_frame, bg=CLR_SURFACE_CONTAINER)
        form_inner.pack(fill="x", padx=16, pady=16)

        tk.Label(form_inner, text="New Habit:", font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE_VARIANT).pack(side="left", padx=(0, 8))
        self.new_habit_entry = self.create_entry(form_inner, width=25)
        self.new_habit_entry.pack(side="left", padx=(0, 8))

        tk.Label(form_inner, text="Frequency:", font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE_CONTAINER, fg=CLR_ON_SURFACE_VARIANT).pack(side="left", padx=(8, 8))
        self.habit_frequency = ttk.Combobox(form_inner,
                                             values=["daily", "weekly", "monthly"],
                                             state="readonly", width=10)
        self.habit_frequency.set("daily")
        self.habit_frequency.pack(side="left", padx=(0, 8))

        self.create_button(form_inner, "+ Add Habit", self.add_habit,
                           primary=True).pack(side="left", padx=8)

        # Habits list
        self.habits_listbox = tk.Listbox(container, height=10,
                                          font=("Segoe UI", 11),
                                          bg=CLR_SURFACE_CONTAINER,
                                          fg=CLR_ON_SURFACE,
                                          selectbackground=CLR_PRIMARY_FIXED,
                                          relief=tk.FLAT, highlightthickness=1,
                                          highlightbackground=CLR_OUTLINE_VARIANT)
        self.habits_listbox.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Action buttons
        complete_frame = tk.Frame(container, bg=CLR_SURFACE)
        complete_frame.pack(fill="x", padx=20)
        self.create_button(complete_frame, "✓ Complete Selected Habit for Today",
                           self.complete_habit, primary=True).pack(side="left", padx=5)
        self.create_button(complete_frame, "🗑 Delete Selected Habit",
                           self.delete_habit, primary=False).pack(side="left", padx=5)

        self.refresh_habits_view()

    def refresh_habits_view(self):
        data = self.load_user_data()
        habits = data.get("habits", [])
        today = datetime.now().date().isoformat()
        completions = data.get("habit_completions", {}).get(today, [])

        self.habits_listbox.delete(0, tk.END)
        for habit in habits:
            habit_id  = habit.get("id")
            completed = "✅" if habit_id in completions else "⬜"
            freq      = habit.get("frequency", "daily")
            streak    = habit.get("streak", 0)
            self.habits_listbox.insert(
                tk.END,
                f"  {completed}  {habit.get('name', '')}  [{freq}]  🔥 {streak}")

    def add_habit(self):
        name = self.new_habit_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a habit name.")
            return
        data = self.load_user_data()
        habits = data.get("habits", [])
        habits.append({
            "id":             self.next_id(habits),
            "name":           name,
            "frequency":      self.habit_frequency.get(),
            "streak":         0,
            "longest_streak": 0,
            "created_at":     _now_iso()
        })
        data["habits"] = habits
        self.save_user_data(data)
        self.new_habit_entry.delete(0, tk.END)
        self.refresh_habits_view()
        messagebox.showinfo("Success", f"Habit '{name}' added!")

    def complete_habit(self):
        selection = self.habits_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a habit to complete.")
            return
        data = self.load_user_data()
        habits = data.get("habits", [])
        today = datetime.now().date().isoformat()
        completions = data.get("habit_completions", {}).get(today, [])

        selected_text = self.habits_listbox.get(selection[0])
        parts = selected_text.split("  ")
        if len(parts) >= 3:
            habit_name = parts[2].split(" [")[0]
            for habit in habits:
                if habit.get("name") == habit_name:
                    habit_id = habit.get("id")
                    if habit_id not in completions:
                        completions.append(habit_id)
                        habit["streak"] = habit.get("streak", 0) + 1
                        if habit["streak"] > habit.get("longest_streak", 0):
                            habit["longest_streak"] = habit["streak"]
                        self._add_xp(25)
                        self._show_notification("🎯 Habit complete! +25 XP")
                    break

        data["habit_completions"][today] = completions
        self.save_user_data(data)
        self.refresh_habits_view()
        self.refresh_dashboard()

    def delete_habit(self):
        selection = self.habits_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a habit to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this habit?"):
            return
        data = self.load_user_data()
        habits = data.get("habits", [])
        selected_text = self.habits_listbox.get(selection[0])
        parts = selected_text.split("  ")
        if len(parts) >= 3:
            habit_name = parts[2].split(" [")[0]
            data["habits"] = [h for h in habits if h.get("name") != habit_name]
            self.save_user_data(data)
            self.refresh_habits_view()
            messagebox.showinfo("Success", "Habit deleted.")