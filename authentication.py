import hashlib
import json
import re
import tkinter as tk
from tkinter import messagebox
 
from constant import (
    CLR_SURFACE, CLR_PRIMARY, CLR_PRIMARY_CONTAINER, CLR_PRIMARY_FIXED,
    CLR_ON_PRIMARY, CLR_ON_SURFACE, CLR_ON_SURFACE_VARIANT, CLR_OUTLINE_VARIANT,
)
 
 
class AuthMixin:
    """Mixin providing user authentication methods."""
 
    # ── Static helpers ──────────────────────────────────────────────────────
 
    @staticmethod
    def hash_password(pw):
        return hashlib.sha256(pw.encode()).hexdigest()
 
    # ── User file I/O ────────────────────────────────────────────────────────
 
    def load_users(self):
        users = {}
        if not self.users_file.exists():
            return users
        with open(self.users_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    users[rec["username"].strip().lower()] = rec
                except:
                    pass
        return users
 
    def save_user(self, username, email, pw_hash):
        rec = {"username": username.strip(), "email": email.strip(),
               "password_hash": pw_hash}
        with open(self.users_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
 
    # ── Login screen ─────────────────────────────────────────────────────────
 
    def show_login(self):
        self.clear_window()
        self.root.configure(bg=CLR_SURFACE)
 
        left = tk.Frame(self.root, bg=CLR_PRIMARY, width=350)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        brand = tk.Frame(left, bg=CLR_PRIMARY)
        brand.pack(expand=True)
        logo = tk.Frame(brand, bg=CLR_ON_PRIMARY, width=60, height=60)
        logo.pack(pady=20)
        logo.pack_propagate(False)
        tk.Label(logo, text="V", font=("Segoe UI", 28, "bold"),
                 bg=CLR_ON_PRIMARY, fg=CLR_PRIMARY).pack(expand=True)
        tk.Label(brand, text="VIAM CENTRIC",
                 font=("Segoe UI", 24, "bold"),
                 bg=CLR_PRIMARY, fg=CLR_ON_PRIMARY).pack()
        tk.Label(brand, text="Personal Scheduler",
                 font=("Segoe UI", 12),
                 bg=CLR_PRIMARY, fg=CLR_PRIMARY_FIXED).pack()
 
        right = tk.Frame(self.root, bg=CLR_SURFACE)
        right.pack(side="left", fill="both", expand=True)
        card = self.create_card(right, bg=CLR_SURFACE, border=True)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=400)
 
        tk.Label(card, text="Welcome Back",
                 font=("Segoe UI", 24, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE).pack(pady=(32, 8))
        tk.Label(card, text="Sign in to continue",
                 font=("Segoe UI", 10),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(pady=(0, 24))
 
        for lbl, kw in [("Username", {}), ("Password", {"show": "*"})]:
            tk.Label(card, text=lbl, font=("Segoe UI", 9, "bold"),
                     bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(
                         anchor="w", padx=32, pady=(8, 4))
            e = self.create_entry(card, width=30, **kw)
            e.pack(padx=32, pady=(0, 12), fill="x")
            if lbl == "Username":
                u_e = e
            else:
                p_e = e
 
        bf = tk.Frame(card, bg=CLR_SURFACE)
        bf.pack(pady=16)
        self.create_button(bf, "Sign In",
                           lambda: self.login(u_e.get(), p_e.get()),
                           primary=True).pack(side="left", padx=6)
        self.create_button(bf, "Create Account",
                           self.show_register,
                           primary=False).pack(side="left", padx=6)
        u_e.bind("<Return>", lambda e: self.login(u_e.get(), p_e.get()))
        p_e.bind("<Return>", lambda e: self.login(u_e.get(), p_e.get()))
 
    # ── Register screen ───────────────────────────────────────────────────────
 
    def show_register(self):
        self.clear_window()
        self.root.configure(bg=CLR_SURFACE)
        left = tk.Frame(self.root, bg=CLR_PRIMARY, width=350)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        right = tk.Frame(self.root, bg=CLR_SURFACE)
        right.pack(side="left", fill="both", expand=True)
        card = self.create_card(right, bg=CLR_SURFACE, border=True)
        card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=520)
        tk.Label(card, text="Create Account",
                 font=("Segoe UI", 24, "bold"),
                 bg=CLR_SURFACE, fg=CLR_ON_SURFACE).pack(pady=(24, 8))
        fields = {}
        for lbl in ["Username", "Email", "Password", "Confirm Password"]:
            tk.Label(card, text=lbl, font=("Segoe UI", 9, "bold"),
                     bg=CLR_SURFACE, fg=CLR_ON_SURFACE_VARIANT).pack(
                         anchor="w", padx=32, pady=(8, 4))
            e = self.create_entry(card, width=30,
                                  show="*" if "Password" in lbl else "")
            e.pack(padx=32, pady=(0, 8), fill="x")
            fields[lbl] = e
        self.create_button(card, "Register",
                           lambda: self.register(
                               fields["Username"].get(),
                               fields["Email"].get(),
                               fields["Password"].get(),
                               fields["Confirm Password"].get()),
                           primary=True).pack(pady=16)
        tk.Button(card, text="← Back to Sign In",
                  command=self.show_login,
                  bg=CLR_SURFACE, fg=CLR_PRIMARY,
                  relief=tk.FLAT, cursor="hand2",
                  font=("Segoe UI", 9)).pack()
 
    # ── Auth logic ────────────────────────────────────────────────────────────
 
    def login(self, username, password):
        username = username.strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        ud = self.load_users().get(username.lower())
        if not ud or self.hash_password(password) != ud["password_hash"]:
            messagebox.showerror("Error", "Invalid username or password.")
            return
        self.current_user = {"username": ud["username"]}
        self.show_main()
 
    def register(self, username, email, password, confirm):
        username, email = username.strip(), email.strip()
        if not all([username, email, password]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        if not re.match(r"^[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email address.")
            return
        if username.lower() in self.load_users():
            messagebox.showerror("Error", "Username already exists.")
            return
        self.save_user(username, email, self.hash_password(password))
        messagebox.showinfo("Success", "Account created! Please sign in.")
        self.show_login()
 
    def logout(self):
        if self.timer_update_job:
            try:
                self.root.after_cancel(self.timer_update_job)
            except:
                pass
        self.current_user = None
        self.show_login()