import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, timedelta
from db import fetch_all, execute_query

class TransactionsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.selected_transaction_id = None
        self.create_widgets()
        self.load_transactions()

    def create_widgets(self):
        tk.Label(self, text="🔁 Transactions", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        self.user_id_var = tk.StringVar()
        self.book_id_var = tk.StringVar()
        self.issue_date_var = tk.StringVar()
        self.due_date_var = tk.StringVar()
        self.return_date_var = tk.StringVar()

        # Set today's date to issue_date_var
        today = date.today()
        self.issue_date_var.set(today.strftime("%Y-%m-%d"))

        # Set default due date to today + 14 days
        due_date_default = today + timedelta(days=14)
        self.due_date_var.set(due_date_default.strftime("%Y-%m-%d"))

        self.users = fetch_all("SELECT user_id, name FROM users")
        self.books = fetch_all("SELECT book_id, title FROM books")

        user_options = [user[1] for user in self.users]
        book_options = [book[1] for book in self.books]

        labels = ["User", "Book", "Issue Date (YYYY-MM-DD)", "Due Date", "Return Date"]
        vars = [self.user_id_var, self.book_id_var, self.issue_date_var, self.due_date_var, self.return_date_var]

        for i in range(len(labels)):
            tk.Label(form_frame, text=labels[i], bg="white").grid(row=i, column=0, sticky="w", pady=2)
            if i == 0:
                ttk.Combobox(form_frame, textvariable=self.user_id_var, values=user_options, state="readonly").grid(row=i, column=1, pady=2)
            elif i == 1:
                ttk.Combobox(form_frame, textvariable=self.book_id_var, values=book_options, state="readonly").grid(row=i, column=1, pady=2)
            else:
                DateEntry(form_frame, textvariable=vars[i], date_pattern='yyyy-mm-dd').grid(row=i, column=1, pady=2)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Transaction", command=self.add_transaction,
                  bg="#2980b9", fg="white", width=16).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Edit Transaction", command=self.edit_transaction,
                  bg="#f39c12", fg="white", width=16).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Delete Transaction", command=self.delete_transaction,
                  bg="#e74c3c", fg="white", width=16).grid(row=0, column=2, padx=5)

        self.tree = ttk.Treeview(self, columns=("ID", "User", "Book", "Issue", "Due", "Return", "Fine"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=10, fill="x", padx=20)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = """
            SELECT t.transaction_id, u.name AS user_name, b.title AS book_title, 
                   t.issue_date, t.due_date, t.return_date, f.amount
            FROM transactions t
            JOIN users u ON t.user_id = u.user_id
            JOIN books b ON t.book_id = b.book_id
            LEFT JOIN fines f ON t.fine_id = f.fine_id
        """
        results = fetch_all(query)
        for row in results:
            self.tree.insert("", "end", values=row)

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.selected_transaction_id = values[0]
            self.user_id_var.set(values[1])
            self.book_id_var.set(values[2])
            self.issue_date_var.set(values[3])
            self.due_date_var.set(values[4])
            self.return_date_var.set(values[5])

    def add_transaction(self):
        try:
            user_name = self.user_id_var.get()
            book_title = self.book_id_var.get()
            issue_date = self.issue_date_var.get()
            due_date = self.due_date_var.get()
            return_date = self.return_date_var.get()

            user_id = next((user[0] for user in self.users if user[1] == user_name), None)
            book_id = next((book[0] for book in self.books if book[1] == book_title), None)

            if not user_id or not book_id:
                messagebox.showerror("Error", "Invalid user or book selection.")
                return

        #  Check if user has any pending fine
            user_fines = fetch_all("""
               SELECT SUM(f.amount) 
               FROM transactions t
               JOIN fines f ON t.fine_id = f.fine_id
               WHERE t.user_id = %s AND f.amount > 0
               """, (user_id,))
            if user_fines and user_fines[0][0]:
               messagebox.showwarning("Pending Fine", f"User '{user_name}' has pending fine of ${user_fines[0][0]:.2f}. Cannot issue new book.")
               return

        # ➡️ Check duplicate book issuance
            duplicate_check = fetch_all("SELECT * FROM transactions WHERE user_id = %s AND book_id = %s", (user_id, book_id))
            if duplicate_check:
                 messagebox.showwarning("Duplicate", "This user has already issued this book.")
                 return

        # Check available copies
            total_copies = fetch_all("SELECT available_copies FROM books WHERE book_id = %s", (book_id,))[0][0]
            issued_copies = fetch_all("SELECT COUNT(*) FROM transactions WHERE book_id = %s", (book_id,))[0][0]
            if total_copies - issued_copies <= 0:
                messagebox.showwarning("Unavailable", f"'{book_title}' is not available right now.")
                return

        # ➡️ Add new transaction
            last_transaction = fetch_all("SELECT MAX(transaction_id) FROM transactions")
            transaction_id = last_transaction[0][0] + 1 if last_transaction[0][0] else 1

            query = """INSERT INTO transactions (transaction_id, user_id, book_id, issue_date, due_date, return_date, fine_id)
                        VALUES (%s, %s, %s, %s, %s, %s, NULL)"""
            execute_query(query, (transaction_id, user_id, book_id, issue_date, due_date, return_date))

            messagebox.showinfo("Success", f"Transaction {transaction_id} added!")
            self.load_transactions()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("Select", "Select a transaction to edit.")
            return
        try:
            user_id = next(user[0] for user in self.users if user[1] == self.user_id_var.get())
            book_id = next(book[0] for book in self.books if book[1] == self.book_id_var.get())

            query = """UPDATE transactions
                       SET user_id=%s, book_id=%s, issue_date=%s, due_date=%s, return_date=%s
                       WHERE transaction_id=%s"""
            execute_query(query, (
                user_id, book_id,
                self.issue_date_var.get(),
                self.due_date_var.get(),
                self.return_date_var.get(),
                self.selected_transaction_id
            ))

            messagebox.showinfo("Updated", "Transaction updated successfully!")
            self.load_transactions()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("Select", "Select a transaction to delete.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?")
        if confirm:
            try:
                execute_query("DELETE FROM transactions WHERE transaction_id=%s", (self.selected_transaction_id,))
                messagebox.showinfo("Deleted", "Transaction deleted.")
                self.load_transactions()
                self.selected_transaction_id = None
            except Exception as e:
                messagebox.showerror("Error", str(e))
