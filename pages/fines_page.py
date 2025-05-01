# pages/fines_page.py

import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all, execute_query

class FinesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.create_widgets()
        self.load_fines()

    def create_widgets(self):
        tk.Label(self, text="💳 Fines Management", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.user_id_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.status_var = tk.StringVar()

        # Fetch users
        self.users = fetch_all("SELECT user_id, name FROM users")
        user_options = [f"{user[0]} - {user[1]}" for user in self.users]

        # Labels and inputs
        tk.Label(form_frame, text="User", bg="white").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(form_frame, textvariable=self.user_id_var, values=user_options, state="readonly").grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Amount", bg="white").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(form_frame, textvariable=self.amount_var).grid(row=1, column=1, pady=2)

        tk.Label(form_frame, text="Status (paid/unpaid)", bg="white").grid(row=2, column=0, sticky="w", pady=2)
        tk.Entry(form_frame, textvariable=self.status_var).grid(row=2, column=1, pady=2)

        # Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Fine", command=self.add_fine, bg="#d35400", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update Status", command=self.update_status, bg="#16a085", fg="white", width=14).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Fine", command=self.delete_fine, bg="#c0392b", fg="white", width=12).grid(row=0, column=2, padx=5)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("ID", "User ID", "User Name", "Amount", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)
        self.tree.pack(pady=10, fill="x", padx=20)

    def load_fines(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = """
            SELECT f.fine_id, u.user_id, u.name, f.amount, f.status
            FROM fines f
            JOIN users u ON f.user_id = u.user_id
        """
        results = fetch_all(query)
        for row in results:
            self.tree.insert("", "end", values=row)

    def add_fine(self):
        try:
            # Step 1: Generate a new Fine ID (max + 1)
            result = fetch_all("SELECT MAX(fine_id) FROM fines")
            max_id = result[0][0] if result[0][0] is not None else 0
            new_fine_id = max_id + 1

            # Step 2: Get user ID
            selected_user = self.user_id_var.get()
            user_id = int(selected_user.split(" - ")[0])

            # Step 3: Insert into database with generated Fine ID
            insert_query = "INSERT INTO fines (fine_id, user_id, amount, status) VALUES (%s, %s, %s, %s)"
            params = (
               new_fine_id,
               user_id,
               float(self.amount_var.get()),
               self.status_var.get()
               )
            execute_query(insert_query, params)

            messagebox.showinfo("Success", f"Fine added successfully! Fine ID: {new_fine_id}")
            self.load_fines()
            # Clear input fields
            self.user_id_var.set("")
            self.amount_var.set("")
            self.status_var.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a fine to update.")
            return
        fine_id = self.tree.item(selected[0])["values"][0]
        new_status = self.status_var.get()
        try:
            query = "UPDATE fines SET status = %s WHERE fine_id = %s"
            execute_query(query, (new_status, fine_id))
            messagebox.showinfo("Updated", "Fine status updated.")
            self.load_fines()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_fine(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a fine to delete.")
            return
        fine_id = self.tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Fine ID {fine_id}?")
        if confirm:
            try:
                execute_query("DELETE FROM fines WHERE fine_id = %s", (fine_id,))
                messagebox.showinfo("Deleted", f"Fine ID {fine_id} deleted.")
                self.load_fines()
            except Exception as e:
                messagebox.showerror("Error", str(e))
