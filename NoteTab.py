"""
VIAM CENTRIC - Notes Tab
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER,
    CLR_PRIMARY, CLR_TERTIARY,
    CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT,
    CLR_OUTLINE_VARIANT,
)


class NotesMixin:
    """Mixin providing the Notes/Notepad tab."""

    def build_notes_tab(self):
        outer = tk.Frame(self.notes_tab, bg=CLR_SURFACE)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_section_header(outer, "Daily Notepad", "📝", CLR_TERTIARY)
        tk.Label(outer,
                 text="Select a date and write anything — ideas, meeting notes, journaling.",
                 font=("Segoe UI", 10), bg=CLR_SURFACE,
                 fg=CLR_ON_SURFACE_VARIANT).pack(anchor="w", padx=20, pady=(0, 12))

        date_row = tk.Frame(outer, bg=CLR_SURFACE)
        date_row.pack(fill="x", padx=20, pady=(0, 12))
        tk.Label(date_row, text="Date:", font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(side="left", padx=(0, 8))
        self.notes_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        notes_date_entry = self.create_entry(date_row, textvariable=self.notes_date_var, width=14)
        notes_date_entry.pack(side="left", padx=(0, 12))
        self.create_button(date_row, "Load", self._load_note, primary=False).pack(side="left", padx=4)
        self.create_button(date_row, "Save", self._save_note, primary=True).pack(side="left", padx=4)
        self.create_button(date_row, "Today",
                           lambda: (self.notes_date_var.set(datetime.now().strftime("%Y-%m-%d")),
                                    self._load_note()),
                           primary=False).pack(side="left", padx=4)

        note_wrap = tk.Frame(outer, bg=CLR_SURFACE,
                              highlightthickness=1,
                              highlightbackground=CLR_OUTLINE_VARIANT)
        note_wrap.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.notes_text = tk.Text(note_wrap,
                                   font=("Segoe UI", 11),
                                   bg=CLR_SURFACE_CONTAINER,
                                   fg=CLR_ON_SURFACE,
                                   insertbackground=CLR_PRIMARY,
                                   relief=tk.FLAT,
                                   padx=16, pady=12,
                                   wrap="word",
                                   highlightthickness=0)
        notes_vsb = ttk.Scrollbar(note_wrap, orient="vertical",
                                   command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_vsb.set)
        notes_vsb.pack(side="right", fill="y")
        self.notes_text.pack(fill="both", expand=True)

        tk.Label(outer, text="Previously saved note dates:",
                 font=("Segoe UI", 9, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(anchor="w", padx=20, pady=(8, 4))
        self.notes_list = tk.Listbox(outer, height=5,
                                      font=("Segoe UI", 9),
                                      bg=CLR_SURFACE_CONTAINER,
                                      fg=CLR_ON_SURFACE,
                                      selectbackground=CLR_SURFACE,
                                      relief=tk.FLAT, highlightthickness=0)
        self.notes_list.pack(fill="x", padx=20, pady=(0, 8))
        self.notes_list.bind("<<ListboxSelect>>", self._on_notes_list_select)

        self._refresh_notes_list()
        self._load_note()

    def _load_note(self):
        date_str = self.notes_date_var.get().strip()
        data = self.load_user_data()
        content = data.get("daily_notes", {}).get(date_str, "")
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", content)

    def _save_note(self):
        date_str = self.notes_date_var.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Date must be YYYY-MM-DD"); return
        data = self.load_user_data()
        content = self.notes_text.get("1.0", tk.END).strip()
        if content:
            data["daily_notes"][date_str] = content
        elif date_str in data["daily_notes"]:
            del data["daily_notes"][date_str]
        self.save_user_data(data)
        self._refresh_notes_list()
        messagebox.showinfo("Saved", f"✅ Note saved for {date_str}")

    def _refresh_notes_list(self):
        data = self.load_user_data()
        dates = sorted(data.get("daily_notes", {}).keys(), reverse=True)
        self.notes_list.delete(0, tk.END)
        for d in dates:
            snippet = data["daily_notes"][d][:50].replace("\n", " ")
            self.notes_list.insert(tk.END, f"  {d}  —  {snippet}…")

    def _on_notes_list_select(self, _):
        sel = self.notes_list.curselection()
        if not sel:
            return
        line = self.notes_list.get(sel[0])
        date_str = line.strip()[:10]
        self.notes_date_var.set(date_str)
        self._load_note()