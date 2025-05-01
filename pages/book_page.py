import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all, execute_query

class BooksPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.categories = {}
        self.publishers = {}
        self.create_widgets()
        self.load_books()

    def create_widgets(self):
        tk.Label(self, text="📘 Book Management", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.isbn_var = tk.StringVar()
        self.pub_year_var = tk.StringVar()
        self.copies_var = tk.StringVar()

        # Category and Publisher will use dropdowns
        self.category_var = tk.StringVar()
        self.publisher_var = tk.StringVar()

        # Labels and Entry fields
        labels = ["Title", "Author", "ISBN", "Category", "Publisher", "Publication Year", "Copies"]
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, bg="white").grid(row=i, column=0, sticky="w", pady=2)

        tk.Entry(form_frame, textvariable=self.title_var).grid(row=0, column=1, pady=2)
        tk.Entry(form_frame, textvariable=self.author_var).grid(row=1, column=1, pady=2)
        tk.Entry(form_frame, textvariable=self.isbn_var).grid(row=2, column=1, pady=2)

        # Dropdowns for category and publisher
        self.category_dropdown = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly")
        self.category_dropdown.grid(row=3, column=1, pady=2)

        self.publisher_dropdown = ttk.Combobox(form_frame, textvariable=self.publisher_var, state="readonly")
        self.publisher_dropdown.grid(row=4, column=1, pady=2)

        tk.Entry(form_frame, textvariable=self.pub_year_var).grid(row=5, column=1, pady=2)
        tk.Entry(form_frame, textvariable=self.copies_var).grid(row=6, column=1, pady=2)

        # Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Book", command=self.add_book, bg="#27ae60", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected, bg="#c0392b", fg="white", width=15).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Update Selected", command=self.update_selected, bg="#2980b9", fg="white", width=15).grid(row=0, column=2, padx=5)
        # Table
        self.tree = ttk.Treeview(self, columns=("ID", "Title", "Author", "ISBN", "Category", "Publisher", "Year", "Copies"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10, fill="x", padx=20)

        # Load dropdown values
        self.load_dropdowns()

    def load_dropdowns(self):
        # Load categories
        cat_results = fetch_all("SELECT category_id, category_name FROM categories")
        self.categories = {name: cid for cid, name in cat_results}
        self.category_dropdown['values'] = list(self.categories.keys())

        # Load publishers
        pub_results = fetch_all("SELECT publisher_id, publisher_name FROM publishers")
        self.publishers = {name: pid for pid, name in pub_results}
        self.publisher_dropdown['values'] = list(self.publishers.keys())

    def load_books(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        query = """SELECT b.book_id, b.title, b.author, b.isbn, c.category_name, p.publisher_name, 
                          b.publication_year, b.available_copies
                   FROM books b
                   LEFT JOIN categories c ON b.category_id = c.category_id
                   LEFT JOIN publishers p ON b.publisher_id = p.publisher_id"""
        results = fetch_all(query)
        for row in results:
            self.tree.insert("", "end", values=row)

    def add_book(self):
        try:
            # Get selected category and publisher IDs
            category_id = self.categories.get(self.category_var.get())
            publisher_id = self.publishers.get(self.publisher_var.get())

            if not category_id or not publisher_id:
                messagebox.showerror("Error", "Please select valid category and publisher.")
                return

            # Generate book ID manually
            result = fetch_all("SELECT MAX(book_id) FROM books")
            next_book_id = (result[0][0] or 0) + 1

            query = """INSERT INTO books (book_id, title, author, isbn, category_id, publisher_id, publication_year, available_copies)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            params = (
                next_book_id,
                self.title_var.get(),
                self.author_var.get(),
                self.isbn_var.get(),
                category_id,
                publisher_id,
                int(self.pub_year_var.get()),
                int(self.copies_var.get())
            )

            execute_query(query, params)
            messagebox.showinfo("Success", f"Book added successfully with ID {next_book_id}!")
            self.load_books()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a book to delete.")
            return
        book_id = self.tree.item(selected[0])['values'][0]
        try:
            execute_query("DELETE FROM books WHERE book_id = %s", (book_id,))
            messagebox.showinfo("Deleted", "Book deleted successfully!")
            self.load_books()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def update_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a book to update.")
            return
        book_id = self.tree.item(selected[0])['values'][0]

        # Get selected category and publisher IDs
        category_id = self.categories.get(self.category_var.get())
        publisher_id = self.publishers.get(self.publisher_var.get())

        if not category_id or not publisher_id:
            messagebox.showerror("Error", "Please select valid category and publisher.")
            return

        query = """UPDATE books SET title=%s, author=%s, isbn=%s, category_id=%s, publisher_id=%s,
                   publication_year=%s, available_copies=%s WHERE book_id=%s"""
        params = (
            self.title_var.get(),
            self.author_var.get(),
            self.isbn_var.get(),
            category_id,
            publisher_id,
            int(self.pub_year_var.get()),
            int(self.copies_var.get()),
            book_id
        )
        try:
            execute_query(query, params)
            messagebox.showinfo("Success", "Book updated successfully!")
            self.load_books()
        except Exception as e:
            messagebox.showerror("Error", str(e))