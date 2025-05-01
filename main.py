import tkinter as tk
from pages.dashboard import DashboardPage
from pages.book_page import BooksPage
from pages.users_page import UsersPage
from pages.transactions_page import TransactionsPage
from pages.reservations_page import ReservationsPage
from pages.fines_page import FinesPage
from pages.search_page import SearchPage
from pages.category_page import CategoryPage
from pages.publisher_page import PublisherPage
class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 Public Library Management System")
        self.geometry("1100x650")
        self.configure(bg="#f9f9f9")

        self.sidebar_visible = True
        self.sidebar = None
        self.sidebar_buttons_frame = None

        self.create_sidebar()
        self.create_container()
        self.show_page("Dashboard")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")

        # Hamburger button
        toggle_frame = tk.Frame(self.sidebar, bg="#2c3e50")
        toggle_frame.pack(pady=15)
        self.toggle_button = tk.Button(
            toggle_frame, text="☰", font=("Arial", 18), bg="#2c3e50", fg="white",
            relief="flat", command=self.toggle_sidebar
        )
        self.toggle_button.pack()

        # Buttons Frame
        self.sidebar_buttons_frame = tk.Frame(self.sidebar, bg="#2c3e50")
        self.sidebar_buttons_frame.pack(fill="both", expand=True, pady=15)

        buttons = [
            ("🏠 Dashboard", "Dashboard"),
            ("📂 Categories", "Categories"),
            ("🏢 Publishers", "Publishers"),
            ("📘 Books", "Books"),
            ("👥 Users", "Users"),
            ("🔁 Transactions", "Transactions"),
            ("📅 Reservations", "Reservations"),
            ("💸 Fines", "Fines"),
            ("🔍 Search", "Search"),
        ]

        for text, page_name in buttons:
            button = tk.Button(
                self.sidebar_buttons_frame, text=text, fg="white", bg="#34495e",
                activebackground="#1abc9c", activeforeground="white",
                relief="flat", font=("Segoe UI", 11, "bold"),
                anchor="w", padx=20,
                command=lambda name=page_name: self.show_page(name)
            )
            button.pack(fill="x", pady=10, padx=8)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar_buttons_frame.forget()
            self.sidebar.config(width=60)
            self.toggle_button.config(text="☰")
        else:
            self.sidebar_buttons_frame.pack(fill="both", expand=True, pady=10)
            self.sidebar.config(width=200)
            self.toggle_button.config(text="☰")
        self.sidebar_visible = not self.sidebar_visible

    def create_container(self):
        self.container = tk.Frame(self, bg="white")
        self.container.pack(side="right", fill="both", expand=True)

    def show_page(self, page_name):
        # Clear current page
        for widget in self.container.winfo_children():
            widget.destroy()

        # Lazy load pages
        page = None
        if page_name == "Dashboard":
            page = DashboardPage(self.container)
        elif page_name == "Categories":
            page = CategoryPage(self.container)
        elif page_name == "Publishers":
            page = PublisherPage(self.container)
        elif page_name == "Books":
            page = BooksPage(self.container)
        elif page_name == "Users":
            page = UsersPage(self.container)
        elif page_name == "Transactions":
            page = TransactionsPage(self.container)
        elif page_name == "Reservations":
            page = ReservationsPage(self.container)
        elif page_name == "Fines":
            page = FinesPage(self.container)
        elif page_name == "Search":
            page = SearchPage(self.container)

        if page:
            page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
