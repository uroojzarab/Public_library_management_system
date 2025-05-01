import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all, execute_query

class ReservationsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.selected_reservation_id = None
        self.create_widgets()
        self.load_reservations()

    def create_widgets(self):
        tk.Label(self, text="📚 Book Reservations", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.user_var = tk.StringVar()
        self.book_var = tk.StringVar()
        self.reservation_date_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.users = fetch_all("SELECT user_id, name FROM users")
        self.books = fetch_all("SELECT book_id, title FROM books")

        user_options = [f"{user[1]} ({user[0]})" for user in self.users]
        book_options = [f"{book[1]} ({book[0]})" for book in self.books]
        status_options = ["Pending", "Approved", "expired"]

        labels = ["User", "Book", "Reservation Date (YYYY-MM-DD)", "Status"]
        values = [self.user_var, self.book_var, self.reservation_date_var, self.status_var]
        dropdown_values = [user_options, book_options, None, status_options]

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, bg="white").grid(row=i, column=0, sticky="w", pady=2)
            if dropdown_values[i]:
                ttk.Combobox(form_frame, textvariable=values[i], values=dropdown_values[i], state="readonly").grid(row=i, column=1, pady=2)
            else:
                tk.Entry(form_frame, textvariable=values[i]).grid(row=i, column=1, pady=2)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Reservation", command=self.add_reservation, bg="#8e44ad", fg="white", width=16).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update Status", command=self.update_status, bg="#f39c12", fg="white", width=14).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame,text="Delete", command=self.delete_selected, bg="#c0392b", fg="white", width=15).grid(row=0, column=2, padx=5)
        self.tree = ttk.Treeview(self, columns=("ID", "User", "Book", "Date", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)
        self.tree.pack(pady=10, fill="x", padx=20)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_reservations(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = """
            SELECT r.reservation_id, u.name, b.title, r.reservation_date, r.status
            FROM reservations r
            JOIN users u ON r.user_id = u.user_id
            JOIN books b ON r.book_id = b.book_id
        """
        results = fetch_all(query)
        for row in results:
            self.tree.insert("", "end", values=row)

    def get_id_from_selection(self, selection):
        if "(" in selection and ")" in selection:
            return int(selection.split("(")[-1].replace(")", ""))
        return None

    def add_reservation(self):
        try:
            user_id = self.get_id_from_selection(self.user_var.get())
            book_id = self.get_id_from_selection(self.book_var.get())
            reservation_date = self.reservation_date_var.get()
            status = self.status_var.get()

            # Auto-generate reservation_id if not auto-incremented in DB
            reservation_id = fetch_all("SELECT MAX(reservation_id) FROM reservations")[0][0]
            reservation_id = (reservation_id + 1) if reservation_id else 1

            query = """INSERT INTO reservations (reservation_id, user_id, book_id, reservation_date, status)
                       VALUES (%s, %s, %s, %s, %s)"""
            execute_query(query, (reservation_id, user_id, book_id, reservation_date, status))
            messagebox.showinfo("Success", f"Reservation #{reservation_id} added successfully!")
            self.load_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def update_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a reservation", "Please select a reservation to update.")
            return
        reservation_id = self.tree.item(selected[0])["values"][0]
        new_status = self.status_var.get()
        try:
            query = "UPDATE reservations SET status = %s WHERE reservation_id = %s"
            execute_query(query, (new_status, reservation_id))
            messagebox.showinfo("Updated", "Status updated successfully.")
            self.load_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.selected_reservation_id = values[0]
            self.user_var.set(f"{values[1]} ({self.get_user_id_by_name(values[1])})")
            self.book_var.set(f"{values[2]} ({self.get_book_id_by_title(values[2])})")
            self.reservation_date_var.set(values[3])
            self.status_var.set(values[4])

    def get_user_id_by_name(self, name):
        for user in self.users:
            if user[1] == name:
                return user[0]
        return None

    def get_book_id_by_title(self, title):
        for book in self.books:
            if book[1] == title:
                return book[0]
        return None

    def edit_reservation(self):
        if self.selected_reservation_id is None:
            messagebox.showwarning("Select a reservation", "Please select a reservation to edit.")
            return
        try:
            user_id = self.get_id_from_selection(self.user_var.get())
            book_id = self.get_id_from_selection(self.book_var.get())
            reservation_date = self.reservation_date_var.get()
            status = self.status_var.get()

            query = """UPDATE reservations 
                       SET user_id = %s, book_id = %s, reservation_date = %s, status = %s 
                       WHERE reservation_id = %s"""
            execute_query(query, (user_id, book_id, reservation_date, status, self.selected_reservation_id))
            messagebox.showinfo("Success", "Reservation updated successfully!")
            self.load_reservations()
            self.selected_reservation_id = None
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a reservation to delete.")
            return
        reservation_id = self.tree.item(selected[0])['values'][0]
        try:
            execute_query("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))
            messagebox.showinfo("Deleted", "Reservation deleted successfully!")
            self.load_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            