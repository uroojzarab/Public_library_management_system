import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all, execute_query

class CategoryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.create_widgets()
        self.load_categories()

    def create_widgets(self):
        tk.Label(self, text="📚 Category Management", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.category_id_var = tk.StringVar()
        self.category_name_var = tk.StringVar()

        tk.Label(form_frame, text="Category ID", bg="white").grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(form_frame, textvariable=self.category_id_var).grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Category Name", bg="white").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(form_frame, textvariable=self.category_name_var).grid(row=1, column=1, pady=2)

        tk.Button(form_frame, text="Add Category", command=self.add_category, bg="#8e44ad", fg="white", width=15).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(form_frame, text="Delete Selected", command=self.delete_selected, bg="#c0392b", fg="white", width=15).grid(row=2, column=2, columnspan=2, pady=5)
        tk.Button(form_frame, text="Update Selected", command=self.update_selected, bg="#2980b9", fg="white", width=15).grid(row=2, column=4, columnspan=2, pady=5)
        self.tree = ttk.Treeview(self, columns=("ID", "Name"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.pack(pady=10, fill="x", padx=20)

    def load_categories(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        results = fetch_all("SELECT * FROM categories")
        for row in results:
            self.tree.insert("", "end", values=row)

    def add_category(self):
        try:
            query = "INSERT INTO categories (category_id, category_name) VALUES (%s, %s)"
            params = (self.category_id_var.get(), self.category_name_var.get())
            execute_query(query, params)
            messagebox.showinfo("Success", "Category added successfully!")
            self.load_categories()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def delete_selected(self):
        try:
            selected_item = self.tree.selection()[0]
            category_id = self.tree.item(selected_item, "values")[0]
            query = "DELETE FROM categories WHERE category_id = %s"
            params = (category_id,)
            execute_query(query, params)
            messagebox.showinfo("Success", "Category deleted successfully!")
            self.load_categories()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def update_selected(self):
        try:
            selected_item = self.tree.selection()[0]
            category_id = self.tree.item(selected_item, "values")[0]
            new_category_name = self.category_name_var.get()
            query = "UPDATE categories SET category_name = %s WHERE category_id = %s"
            params = (new_category_name, category_id)
            execute_query(query, params)
            messagebox.showinfo("Success", "Category updated successfully!")
            self.load_categories()
        except Exception as e:
            messagebox.showerror("Error", str(e))
