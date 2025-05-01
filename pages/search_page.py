# pages/search_page.py

import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all

class SearchPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="🔍 Search Books", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Title")  # Default search by Title

        search_options = ["Title", "Author", "Category"]
        tk.Label(form_frame, text="Search By", bg="white").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(form_frame, textvariable=self.search_by_var, values=search_options, state="readonly").grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Search Term", bg="white").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(form_frame, textvariable=self.search_var).grid(row=1, column=1, pady=2)

        tk.Button(form_frame, text="Search", command=self.search_books, bg="#3498db", fg="white", width=12).grid(row=2, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Title", "Author", "Category", "Publisher", "Year"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)
        self.tree.pack(pady=10, fill="x", padx=20)

    def search_books(self):
        search_term = self.search_var.get()
        search_by = self.search_by_var.get()

        query = "SELECT book_id, title, author, category_name, publisher_name, publication_year FROM books " \
                "JOIN categories ON books.category_id = categories.category_id " \
                "JOIN publishers ON books.publisher_id = publishers.publisher_id WHERE "

        if search_by == "Title":
            query += "title LIKE %s"
            params = (f"%{search_term}%",)
        elif search_by == "Author":
            query += "author LIKE %s"
            params = (f"%{search_term}%",)
        elif search_by == "Category":
            query += "category_name LIKE %s"
            params = (f"%{search_term}%",)

        try:
            results = fetch_all(query, params)
            if results:
                for row in self.tree.get_children():
                    self.tree.delete(row)
                for row in results:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("No Results", "No books found matching your search.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
