import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all, execute_query

class PublisherPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.create_widgets()
        self.load_publishers()

    def create_widgets(self):
        tk.Label(self, text="🏢 Publisher Management", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.publisher_id_var = tk.StringVar()
        self.publisher_name_var = tk.StringVar()

        tk.Label(form_frame, text="Publisher ID", bg="white").grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(form_frame, textvariable=self.publisher_id_var).grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Publisher Name", bg="white").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(form_frame, textvariable=self.publisher_name_var).grid(row=1, column=1, pady=2)

        tk.Button(form_frame, text="Add Publisher", command=self.add_publisher, bg="#2c3e50", fg="white", width=15).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(form_frame, text="Delete Selected", command=self.delete_selected, bg="#c0392b", fg="white", width=15).grid(row=2, column=2, columnspan=2, pady=5)
        tk.Button(form_frame, text="Update Selected", command=self.update_selected, bg="#2980b9", fg="white", width=15).grid(row=2, column=4, columnspan=2, pady=5)
        self.tree = ttk.Treeview(self, columns=("ID", "Name"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.pack(pady=10, fill="x", padx=20)

    def load_publishers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        results = fetch_all("SELECT * FROM publishers")
        for row in results:
            self.tree.insert("", "end", values=row)

    def add_publisher(self):
        try:
            query = "INSERT INTO publishers (publisher_id, publisher_name) VALUES (%s, %s)"
            params = (self.publisher_id_var.get(), self.publisher_name_var.get())
            execute_query(query, params)
            messagebox.showinfo("Success", "Publisher added successfully!")
            self.load_publishers()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def delete_selected(self):
        try:
            selected_item = self.tree.selection()[0]
            publisher_id = self.tree.item(selected_item, "values")[0]
            query = "DELETE FROM publishers WHERE publisher_id = %s"
            params = (publisher_id,)
            execute_query(query, params)
            messagebox.showinfo("Success", "Publisher deleted successfully!")
            self.load_publishers()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def update_selected(self):
        try:
            selected_item = self.tree.selection()[0]
            publisher_id = self.tree.item(selected_item, "values")[0]
            new_name = self.publisher_name_var.get()
            query = "UPDATE publishers SET publisher_name = %s WHERE publisher_id = %s"
            params = (new_name, publisher_id)
            execute_query(query, params)
            messagebox.showinfo("Success", "Publisher updated successfully!")
            self.load_publishers()
        except Exception as e:
            messagebox.showerror("Error", str(e))
