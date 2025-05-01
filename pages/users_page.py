import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all, execute_query

class UsersPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        tk.Label(self, text="👤 User Management", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.user_id_var = tk.StringVar()  # Add user ID variable
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        labels = ["User id", "Name", "Email", "Phone"]
        vars = [self.user_id_var, self.name_var, self.email_var, self.phone_var]

        for i in range(len(labels)):
            tk.Label(form_frame, text=labels[i], bg="white").grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(form_frame, textvariable=vars[i]).grid(row=i, column=1, pady=2)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add User", command=self.add_user, bg="#27ae60", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected, bg="#c0392b", fg="white", width=15).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Update Selected", command=self.update_selected, bg="#2980b9", fg="white", width=15).grid(row=0, column=2, padx=5)

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Email", "Phone"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=10, fill="x", padx=20)

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        results = fetch_all("SELECT * FROM users")
        for row in results:
            self.tree.insert("", "end", values=row)

    def add_user(self):
        try:
            # Get the user ID input by the user
            user_id = self.user_id_var.get()

            # Check if the user ID is valid (non-empty)
            if not user_id:
                messagebox.showerror("Error", "Please provide a User ID.")
                return

            # Check if the user ID already exists in the database
            existing_user = fetch_all("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if existing_user:
                messagebox.showerror("Error", "User ID already exists. Please provide a unique ID.")
                return

            query = "INSERT INTO users (user_id, name, email, phone_no) VALUES (%s, %s, %s, %s)"
            params = (
                user_id,
                self.name_var.get(),
                self.email_var.get(),
                self.phone_var.get()
            )
            execute_query(query, params)
            messagebox.showinfo("Success", "User added successfully!")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a user to delete.")
            return
        user_id = self.tree.item(selected[0])['values'][0]
        try:
            execute_query("DELETE FROM users WHERE user_id = %s", (user_id,))
            messagebox.showinfo("Deleted", "User deleted successfully!")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def update_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a user to update.")
            return
        user_id = self.tree.item(selected[0])['values'][0]
        try:
            query = "UPDATE users SET name = %s, email = %s, phone_no = %s WHERE user_id = %s"
            params = (
                self.name_var.get(),
                self.email_var.get(),
                self.phone_var.get(),
                user_id
            )
            execute_query(query, params)
            messagebox.showinfo("Success", "User updated successfully!")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))