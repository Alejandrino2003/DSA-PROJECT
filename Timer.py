import tkinter as tk
from tkinter import messagebox

from constant import (
    CLR_SURFACE, CLR_SURFACE_CONTAINER_HIGH, CLR_PRIMARY, CLR_ON_PRIMARY,
    CLR_ON_SURFACE_VARIANT, CLR_ON_SURFACE
)


class TimerMixin:
    """Mixin providing all timer/clepsydra functionality."""

    # ── Settings dialog ───────────────────────────────────────────────────────

    def show_timer_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Timer Settings")
        dlg.geometry("450x400")
        dlg.configure(bg=CLR_SURFACE)
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg=CLR_PRIMARY)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙ Timer Settings", font=("Segoe UI", 16, "bold"),
                 bg=CLR_PRIMARY, fg=CLR_ON_PRIMARY).pack(pady=16)

        settings_frame = tk.Frame(dlg, bg=CLR_SURFACE)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(settings_frame, text="🍅 clepsydra Duration (minutes):",
                 font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(anchor="w", pady=(0, 5))
        pomo_minutes = tk.IntVar(value=self.clepsydra_duration // 60)
        pomo_spin = tk.Spinbox(settings_frame, from_=1, to=60, textvariable=pomo_minutes,
                               width=10, font=("Segoe UI", 10),
                               bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_SURFACE)
        pomo_spin.pack(anchor="w", pady=(0, 15))

        tk.Label(settings_frame, text="☕ Short Break (minutes):",
                 font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(anchor="w", pady=(0, 5))
        short_minutes = tk.IntVar(value=self.short_break_duration // 60)
        short_spin = tk.Spinbox(settings_frame, from_=1, to=30, textvariable=short_minutes,
                                width=10, font=("Segoe UI", 10),
                                bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_SURFACE)
        short_spin.pack(anchor="w", pady=(0, 15))

        tk.Label(settings_frame, text="🌿 Long Break (minutes):",
                 font=("Segoe UI", 10, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(anchor="w", pady=(0, 5))
        long_minutes = tk.IntVar(value=self.long_break_duration // 60)
        long_spin = tk.Spinbox(settings_frame, from_=1, to=60, textvariable=long_minutes,
                               width=10, font=("Segoe UI", 10),
                               bg=CLR_SURFACE_CONTAINER_HIGH, fg=CLR_SURFACE)
        long_spin.pack(anchor="w", pady=(0, 15))

        auto_break_var = tk.BooleanVar(value=self.clepsydra_auto_break)
        tk.Checkbutton(settings_frame, text="Auto-start breaks", variable=auto_break_var,
                       bg=CLR_SURFACE, fg=CLR_SURFACE,
                       selectcolor=CLR_SURFACE).pack(anchor="w", pady=(0, 15))

        def save_settings():
            self.clepsydra_duration = pomo_minutes.get() * 60
            self.short_break_duration = short_minutes.get() * 60
            self.long_break_duration = long_minutes.get() * 60
            self.clepsydra_auto_break = auto_break_var.get()
            self.reset_clepsydra()
            data = self.load_user_data()
            if "timer_settings" not in data:
                data["timer_settings"] = {}
            data["timer_settings"]["clepsydra_minutes"] = self.clepsydra_duration // 60
            data["timer_settings"]["short_break_minutes"] = self.short_break_duration // 60
            data["timer_settings"]["long_break_minutes"] = self.long_break_duration // 60
            data["timer_settings"]["auto_break"] = self.clepsydra_auto_break
            self.save_user_data(data)
            dlg.destroy()
            messagebox.showinfo("Settings Saved", "Timer settings updated!")

        btn_frame = tk.Frame(dlg, bg=CLR_SURFACE)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.create_button(btn_frame, "Save Settings", save_settings, primary=True).pack(side="right")
        self.create_button(btn_frame, "Cancel", dlg.destroy, primary=False).pack(side="right", padx=6)

    # ── Timer controls ────────────────────────────────────────────────────────

    def start_clepsydra(self):
        if not self.clepsydra_running:
            if self.clepsydra_remaining == 0:
                if self.current_timer_mode == "clepsydra":
                    self.clepsydra_remaining = self.clepsydra_duration
                elif self.current_timer_mode == "short_break":
                    self.clepsydra_remaining = self.short_break_duration
                elif self.current_timer_mode == "long_break":
                    self.clepsydra_remaining = self.long_break_duration
            self.clepsydra_running = True
            self._update_timer()
            if hasattr(self, 'timer_start_btn'):
                self.timer_start_btn.config(state="disabled")

    def pause_clepsydra(self):
        self.clepsydra_running = False
        if hasattr(self, 'timer_start_btn'):
            self.timer_start_btn.config(state="normal")

    def reset_clepsydra(self):
        self.clepsydra_running = False
        self.clepsydra_remaining = 0
        self.current_timer_mode = "clepsydra"
        if hasattr(self, 'timer_display'):
            self.timer_display.config(text=self._format_time(self.clepsydra_duration))
        if hasattr(self, 'timer_start_btn'):
            self.timer_start_btn.config(state="normal")

    def _format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def _update_timer(self):
        if self.clepsydra_running and self.clepsydra_remaining > 0:
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=self._format_time(self.clepsydra_remaining))
            self.clepsydra_remaining -= 1
            self.timer_update_job = self.root.after(1000, self._update_timer)
        elif self.clepsydra_remaining == 0 and self.clepsydra_running:
            self.clepsydra_running = False
            self._handle_timer_completion()

    def _handle_timer_completion(self):
        if self.current_timer_mode == "clepsydra":
            self.clepsydra_count += 1
            messagebox.showinfo("clepsydra Complete",
                                f"🍅 Great work! clepsydra #{self.clepsydra_count} completed!")
            self._add_xp(10)
            if hasattr(self, 'session_label'):
                self.session_label.config(text=f"Sessions completed: {self.clepsydra_count}")
            if self.clepsydra_auto_break:
                if self.clepsydra_count % 4 == 0:
                    self.current_timer_mode = "long_break"
                    self.clepsydra_remaining = self.long_break_duration
                    messagebox.showinfo("Break Time", "🌿 Time for a long break!")
                else:
                    self.current_timer_mode = "short_break"
                    self.clepsydra_remaining = self.short_break_duration
                    messagebox.showinfo("Break Time", "☕ Take a short break!")
                self.start_clepsydra()
        elif self.current_timer_mode in ["short_break", "long_break"]:
            messagebox.showinfo("Break Complete", "Break is over! Ready for the next clepsydra?")
            self.current_timer_mode = "clepsydra"
            self.clepsydra_remaining = 0
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=self._format_time(self.clepsydra_duration))
        if hasattr(self, 'timer_start_btn'):
            self.timer_start_btn.config(state="normal")

    def switch_timer_mode(self, mode):
        if self.clepsydra_running:
            self.pause_clepsydra()
        self.current_timer_mode = mode
        if mode == "clepsydra":
            self.clepsydra_remaining = 0
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=self._format_time(self.clepsydra_duration))
        elif mode == "short_break":
            self.clepsydra_remaining = 0
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=self._format_time(self.short_break_duration))
        elif mode == "long_break":
            self.clepsydra_remaining = 0
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=self._format_time(self.long_break_duration))

    def set_custom_timer(self, minutes, mode="custom"):
        if self.clepsydra_running:
            self.pause_clepsydra()
        self.current_timer_mode = mode
        self.clepsydra_remaining = minutes * 60
        if hasattr(self, 'timer_display'):
            self.timer_display.config(text=self._format_time(self.clepsydra_remaining))
        if messagebox.askyesno("Start Timer", f"Start {minutes}-minute timer?"):
            self.start_clepsydra()

    def start_countdown(self, minutes, task_name="Task"):
        def countdown(remaining):
            if remaining > 0 and self.clepsydra_running:
                if hasattr(self, 'timer_display'):
                    self.timer_display.config(text=self._format_time(remaining))
                self.timer_update_job = self.root.after(1000, lambda: countdown(remaining - 1))
            elif remaining == 0 and self.clepsydra_running:
                self.clepsydra_running = False
                if hasattr(self, 'timer_display'):
                    self.timer_display.config(text="Time's Up!")
                messagebox.showinfo("Timer Complete", f"'{task_name}' time is up!")
                self.root.bell()
                self._add_xp(5)
                if hasattr(self, 'timer_start_btn'):
                    self.timer_start_btn.config(state="normal")

        if self.clepsydra_running:
            self.pause_clepsydra()
        self.current_timer_mode = "countdown"
        self.clepsydra_remaining = minutes * 60
        self.clepsydra_running = True
        if hasattr(self, 'timer_start_btn'):
            self.timer_start_btn.config(state="disabled")
        countdown(self.clepsydra_remaining)