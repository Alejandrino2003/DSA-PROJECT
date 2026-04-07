"""
VIAM CENTRIC - UI Helpers (Styles, Reusable Widgets)
"""

import tkinter as tk
from tkinter import ttk

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER, CLR_SURFACE_CONTAINER_HIGH,
    CLR_SURFACE_CONTAINER_HIGHEST, CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT,
    CLR_PRIMARY, CLR_PRIMARY_CONTAINER, CLR_PRIMARY_FIXED, CLR_ON_PRIMARY,
    CLR_OUTLINE, CLR_OUTLINE_VARIANT,
)


class UIMixin:
    """Mixin providing reusable widget factory methods and style setup."""

    # ── Styles ────────────────────────────────────────────────────────────────

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=CLR_SURFACE, foreground=CLR_ON_SURFACE)
        style.layout("Hidden.TNotebook.Tab", [])
        style.configure("Hidden.TNotebook",
                        background=CLR_SURFACE,
                        borderwidth=0,
                        tabmargins=[0, 0, 0, 0])
        style.configure("TNotebook", background=CLR_SURFACE, borderwidth=0)
        style.configure("TNotebook.Tab",
                        padding=[20, 10],
                        font=("Segoe UI", 10, "bold"),
                        background=CLR_SURFACE_CONTAINER,
                        foreground=CLR_ON_SURFACE_VARIANT)
        style.map("TNotebook.Tab",
                  background=[("selected", CLR_PRIMARY)],
                  foreground=[("selected", CLR_ON_PRIMARY)])
        style.configure("Treeview", rowheight=36, font=("Segoe UI", 10),
                        background=CLR_SURFACE, foreground=CLR_ON_SURFACE,
                        fieldbackground=CLR_SURFACE, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background=CLR_SURFACE_CONTAINER,
                        foreground=CLR_ON_SURFACE_VARIANT)
        style.configure("Vertical.TScrollbar",
                        background=CLR_SURFACE_CONTAINER_HIGH,
                        troughcolor=CLR_SURFACE, width=8)
        style.configure("TCombobox",
                        background=CLR_SURFACE_CONTAINER_HIGH,
                        fieldbackground=CLR_SURFACE_CONTAINER_HIGH,
                        foreground=CLR_ON_SURFACE)

    # ── Window helpers ────────────────────────────────────────────────────────

    def clear_window(self):
        if self.timer_update_job:
            try:
                self.root.after_cancel(self.timer_update_job)
            except:
                pass
        for job in [self.clock_job, self.quote_job]:
            if job:
                try:
                    self.root.after_cancel(job)
                except:
                    pass
        for w in self.root.winfo_children():
            w.destroy()

    # ── Widget factories ──────────────────────────────────────────────────────

    def create_card(self, parent, bg=CLR_SURFACE, border=True, **kw):
        f = tk.Frame(parent, bg=bg, relief=tk.FLAT, **kw)
        if border:
            f.configure(highlightthickness=1,
                        highlightbackground=CLR_OUTLINE_VARIANT)
        return f

    def create_button(self, parent, text, command, primary=True, **kw):
        if primary:
            return tk.Button(parent, text=text, command=command,
                             bg=CLR_PRIMARY, fg=CLR_ON_PRIMARY,
                             font=("Segoe UI", 10, "bold"),
                             relief=tk.FLAT, cursor="hand2",
                             activebackground=CLR_PRIMARY_CONTAINER,
                             activeforeground=CLR_ON_PRIMARY,
                             padx=16, pady=8, **kw)
        else:
            return tk.Button(parent, text=text, command=command,
                             bg=CLR_SURFACE, fg=CLR_PRIMARY,
                             font=("Segoe UI", 10, "bold"),
                             relief=tk.FLAT, cursor="hand2",
                             activebackground=CLR_PRIMARY_FIXED,
                             activeforeground=CLR_PRIMARY,
                             highlightthickness=1,
                             highlightbackground=CLR_OUTLINE_VARIANT,
                             padx=16, pady=8, **kw)

    def create_entry(self, parent, **kw):
        return tk.Entry(parent,
                        font=("Segoe UI", 10),
                        bg=CLR_SURFACE_CONTAINER_HIGH,
                        fg=CLR_ON_SURFACE,
                        insertbackground=CLR_PRIMARY,
                        relief=tk.FLAT,
                        highlightthickness=1,
                        highlightbackground=CLR_OUTLINE_VARIANT,
                        highlightcolor=CLR_PRIMARY,
                        **kw)

    def create_section_header(self, parent, text, icon="", color=CLR_PRIMARY):
        frame = tk.Frame(parent, bg=parent.cget("bg"))
        frame.pack(fill="x", padx=20, pady=(16, 8))
        tk.Frame(frame, bg=color, width=4, height=24).pack(
            side="left", padx=(0, 12))
        if icon:
            tk.Label(frame, text=icon, font=("Segoe UI", 14),
                     bg=parent.cget("bg")).pack(side="left", padx=(0, 8))
        tk.Label(frame, text=text, font=("Segoe UI", 13, "bold"),
                 bg=parent.cget("bg"), fg=CLR_ON_SURFACE).pack(side="left")
        return frame

    def _scrollable(self, parent):
        canvas = tk.Canvas(parent, bg=CLR_SURFACE, highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=CLR_SURFACE)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=e.width)
        inner.bind("<Configure>", _resize)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)
        return canvas, inner

    # ── Dialog helpers ────────────────────────────────────────────────────────

    def _dlg(self, title, h, color):
        d = tk.Toplevel(self.root)
        d.title(title)
        d.geometry(f"520x{h}")
        d.configure(bg=CLR_SURFACE)
        d.grab_set()
        hdr = tk.Frame(d, bg=color)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=("Segoe UI", 16, "bold"),
                 bg=color, fg=CLR_ON_PRIMARY).pack(anchor="w", padx=20, pady=16)
        form = tk.Frame(d, bg=CLR_SURFACE)
        form.pack(fill="both", expand=True, padx=20, pady=16)
        form.columnconfigure(1, weight=1)
        return d, form

    def _dlg_row(self, form, row, label, widget):
        tk.Label(form, text=label, font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT
                 ).grid(row=row, column=0, sticky="w", pady=8)
        widget.grid(row=row, column=1, sticky="ew", pady=8, padx=(16, 0))

    def _form_grid(self, parent):
        f = tk.Frame(parent, bg=CLR_SURFACE)
        f.pack(fill="x", padx=20, pady=(16, 0))
        f.columnconfigure(1, weight=1)
        return f

    def _frow(self, f, row, label, widget):
        tk.Label(f, text=label, font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT
                 ).grid(row=row, column=0, sticky="w", pady=8)
        widget.grid(row=row, column=1, sticky="ew", pady=8, padx=(16, 0))