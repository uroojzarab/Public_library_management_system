import tkinter as tk
from tkinter import Label
from db import fetch_all

class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f9f9f9")
        self.heading_text = "📊 Library Dashboard"
        self.current_index = 0
        self.create_widgets()

    def create_widgets(self):
        # Placeholder label for animated heading
        self.heading_label = Label(
            self,
            text="",
            font=("Segoe UI", 24, "bold"),
            bg="#f9f9f9",
            fg="#2c3e50"
        )
        self.heading_label.pack(pady=30)

        # Start animation
        self.animate_heading()

        stats = [
            ("📚 Total Books", "SELECT COUNT(*) FROM books"),
            ("👤 Total Users", "SELECT COUNT(*) FROM users"),
            ("📅 Total Reservations", "SELECT COUNT(*) FROM reservations"),
            ("💸 Unpaid Fines", "SELECT COUNT(*) FROM fines WHERE status = 'unpaid'")
        ]

        for label, query in stats:
            value = fetch_all(query)[0][0]
            self.create_card(label, value)

    def animate_heading(self):
        if self.current_index <= len(self.heading_text):
            self.heading_label.config(text=self.heading_text[:self.current_index])
            self.current_index += 1
            self.after(70, self.animate_heading)  # Adjust speed here (ms)

    def create_card(self, label, value):
        card = tk.Frame(
            self,
            bg="#ffffff",
            padx=20,
            pady=15,
            bd=2,
            relief="ridge"
        )
        card.pack(pady=10, ipadx=10, ipady=5, fill="x", padx=80)

        tk.Label(
            card,
            text=label,
            font=("Segoe UI", 14, "bold"),
            bg="#ffffff",
            fg="#34495e",
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            card,
            text=str(value),
            font=("Segoe UI", 20, "bold"),
            fg="#3498db",
            bg="#ffffff",
            anchor="w"
        ).pack(fill="x", pady=(5, 0))
