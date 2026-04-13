"""Tkinter GUI — Personal Expense Tracker (HKD)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date as _today_date
from typing import List, Optional

from models.transaction import Transaction, KIND_INCOME, KIND_EXPENSE
from models.ledger import Ledger
from models.budget import BudgetBook
from storage.json_store import JsonStore

PRESET_CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Entertainment",
    "Health",
    "Education",
    "Utilities",
    "Rent",
    "Salary",
    "Other",
]


class ExpenseTrackerApp(tk.Tk):                                     #Main application class for the Personal Expense Tracker GUI

    def __init__(self, store: JsonStore) -> None:                   #Init function
        super().__init__()
        self.title("Personal Expense Tracker")
        self.resizable(True, True)
        self.minsize(900, 600)

        self._store = store
        self._ledger: Ledger = store.load_ledger()
        self._budget_book: BudgetBook = store.load_budgets()

        self._row_to_tid: dict[str, int] = {}                       #Track row IDs to transaction IDs for deletion

        self._build_ui()
        self._refresh_filter_dropdowns()
        self._refresh_table()


    def _build_ui(self) -> None:                                    #UI buidling
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ---- top: add-transaction form -------------------------------- #
        form_frame = ttk.LabelFrame(self, text="Add Transaction", padding=8)
        form_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self._build_form(form_frame)

        # ---- middle: filter bar + table ------------------------------- #
        center_frame = ttk.Frame(self)
        center_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)
        center_frame.columnconfigure(0, weight=1)
        center_frame.rowconfigure(1, weight=1)

        filter_frame = ttk.LabelFrame(center_frame, text="Filters", padding=6)
        filter_frame.grid(row=0, column=0, sticky="ew")
        self._build_filters(filter_frame)

        table_frame = ttk.LabelFrame(center_frame, text="Transactions", padding=4)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self._build_table(table_frame)

        # ---- bottom: summary + budget --------------------------------- #
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=6)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        summary_frame = ttk.LabelFrame(bottom_frame, text="Summary (filtered view)", padding=8)
        summary_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        self._build_summary(summary_frame)

        budget_frame = ttk.LabelFrame(bottom_frame, text="Budget (selected month)", padding=8)
        budget_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self._build_budget_panel(budget_frame)


    def _build_form(self, parent: ttk.LabelFrame) -> None:                                          #Add transaction form UI construction
        today = str(_today_date.today())

        fields: list[tuple[str, tk.Widget]] = []

        ttk.Label(parent, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="e", padx=4)       #Date label and entry
        self._var_date = tk.StringVar(value=today)
        ttk.Entry(parent, textvariable=self._var_date, width=12).grid(row=0, column=1, padx=4)

        ttk.Label(parent, text="Kind:").grid(row=0, column=2, sticky="e", padx=4)                    #Kind label and dropdown
        self._var_kind = tk.StringVar(value=KIND_EXPENSE)
        kind_cb = ttk.Combobox(
            parent,
            textvariable=self._var_kind,
            values=[KIND_EXPENSE, KIND_INCOME],
            state="readonly",
            width=10,
        )
        kind_cb.grid(row=0, column=3, padx=4)

        ttk.Label(parent, text="Category:").grid(row=0, column=4, sticky="e", padx=4)               #Category label and dropdown
        self._var_category = tk.StringVar()
        self._cat_cb = ttk.Combobox(
            parent,
            textvariable=self._var_category,
            values=PRESET_CATEGORIES,
            width=16,
        )
        self._cat_cb.grid(row=0, column=5, padx=4)

        ttk.Label(parent, text="Amount (HKD):").grid(row=0, column=6, sticky="e", padx=4)           #Amount label and entry
        self._var_amount = tk.StringVar()
        ttk.Entry(parent, textvariable=self._var_amount, width=10).grid(row=0, column=7, padx=4)

        ttk.Label(parent, text="Note:").grid(row=0, column=8, sticky="e", padx=4)                   #Note label and entry
        self._var_note = tk.StringVar()
        ttk.Entry(parent, textvariable=self._var_note, width=18).grid(row=0, column=9, padx=4)

        ttk.Button(parent, text="Add", command=self._on_add).grid(row=0, column=10, padx=(8, 0))    #Add button


    def _build_filters(self, parent: ttk.LabelFrame) -> None:                                       #Filter controls UI construction
        ttk.Label(parent, text="Month (YYYY-MM):").grid(row=0, column=0, sticky="e", padx=4)        #Month filter label and dropdown
        self._var_filter_month = tk.StringVar()
        self._month_cb = ttk.Combobox(
            parent,
            textvariable=self._var_filter_month,
            values=[],
            width=12,
        )
        self._month_cb.grid(row=0, column=1, padx=4)
        self._month_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_table())

        ttk.Label(parent, text="Category:").grid(row=0, column=2, sticky="e", padx=4)               #Category filter label and dropdown
        self._var_filter_cat = tk.StringVar()
        self._filter_cat_cb = ttk.Combobox(
            parent,
            textvariable=self._var_filter_cat,
            values=[],
            state="readonly",
            width=16,
        )
        self._filter_cat_cb.grid(row=0, column=3, padx=4)
        self._filter_cat_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_table())

        ttk.Label(parent, text="Kind:").grid(row=0, column=4, sticky="e", padx=4)                   #Kind filter label and dropdown
        self._var_filter_kind = tk.StringVar(value="All")
        kind_filter = ttk.Combobox(
            parent,
            textvariable=self._var_filter_kind,
            values=["All", KIND_INCOME, KIND_EXPENSE],
            state="readonly",
            width=10,
        )
        kind_filter.grid(row=0, column=5, padx=4)
        kind_filter.bind("<<ComboboxSelected>>", lambda _: self._refresh_table())

        ttk.Button(parent, text="Clear Filters", command=self._clear_filters).grid(                 #Kind filter clear button
            row=0, column=6, padx=(12, 0)
        )


    def _build_table(self, parent: ttk.LabelFrame) -> None:                                          #Transaction table UI construction
        columns = ("tid", "date", "kind", "category", "amount", "note")
        self._tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")

        col_cfg = [
            ("tid", "ID", 40),
            ("date", "Date", 90),
            ("kind", "Kind", 80),
            ("category", "Category", 130),
            ("amount", "Amount (HKD)", 110),
            ("note", "Note", 200),
        ]
        for col_id, heading, width in col_cfg:
            self._tree.heading(col_id, text=heading)
            self._tree.column(col_id, width=width, anchor="w")

        scroll_y = ttk.Scrollbar(parent, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll_y.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")

        self._tree.tag_configure("expense", foreground="#c0392b")                                   #Expense rows in red, income rows in green
        self._tree.tag_configure("income", foreground="#27ae60")

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Button(btn_frame, text="Delete Selected", command=self._on_delete).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete All", command=self._on_delete_all).pack(side="left", padx=4)



    def _build_summary(self, parent: ttk.LabelFrame) -> None:                                         #Summary panel UI construction 
        self._lbl_income = ttk.Label(parent, text="Total Income:  HKD 0.00", foreground="#27ae60")
        self._lbl_income.grid(row=0, column=0, sticky="w", pady=2)

        self._lbl_expense = ttk.Label(parent, text="Total Expense: HKD 0.00", foreground="#c0392b")
        self._lbl_expense.grid(row=1, column=0, sticky="w", pady=2)

        self._lbl_net = ttk.Label(parent, text="Net Balance:   HKD 0.00")
        self._lbl_net.grid(row=2, column=0, sticky="w", pady=2)

        ttk.Separator(parent, orient="horizontal").grid(
            row=3, column=0, sticky="ew", pady=4
        )

        ttk.Label(parent, text="Expense by Category:").grid(row=4, column=0, sticky="w")
        self._cat_list = tk.Text(parent, height=5, width=36, state="disabled", relief="flat")
        self._cat_list.grid(row=5, column=0, sticky="ew")


    def _build_budget_panel(self, parent: ttk.LabelFrame) -> None:                                  #Budget panel UI construction
        selector_frame = ttk.Frame(parent)
        selector_frame.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Label(selector_frame, text="Category:").pack(side="left", padx=(0, 4))
        self._var_budget_category = tk.StringVar()
        self._budget_cat_cb = ttk.Combobox(
            selector_frame,
            textvariable=self._var_budget_category,
            values=[],
            state="readonly",
            width=18,
        )
        self._budget_cat_cb.pack(side="left")

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky="w", pady=(0, 4))
        ttk.Button(btn_frame, text="Set Budget Limit", command=self._on_set_budget).pack(
            side="left", padx=(0, 4)
        )
        ttk.Button(btn_frame, text="Remove Limit", command=self._on_remove_budget).pack(side="left")

        ttk.Label(parent, text="Budget Status (selected month):").grid(row=2, column=0, sticky="w")
        self._budget_text = tk.Text(
            parent, height=6, width=36, state="disabled", relief="flat"
        )
        self._budget_text.grid(row=3, column=0, sticky="ew")
        self._budget_text.tag_configure("over", foreground="#c0392b")
        self._budget_text.tag_configure("ok", foreground="#27ae60")
        self._budget_text.tag_configure("nomonth", foreground="#7f8c8d")


    def _on_add(self) -> None:                                                                      #Event handler for adding a new transaction
        try:
            t = Transaction(
                date=self._var_date.get().strip(),
                kind=self._var_kind.get().strip(),
                category=self._var_category.get().strip(),
                amount=self._var_amount.get().strip(),
                note=self._var_note.get().strip(),
            )
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            return

        self._ledger.add(t)
        self._store.save_ledger(self._ledger)
        self._var_amount.set("")
        self._var_note.set("")
        self._refresh_filter_dropdowns()
        self._refresh_table()

    def _on_delete(self) -> None:                                                                   #Delete selected transaction after confirmation
        selected = self._tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a transaction to delete.")
            return
        row_id = selected[0]
        tid = self._row_to_tid.get(row_id)
        if tid is None:
            return
        if not messagebox.askyesno("Confirm Delete", "Delete the selected transaction?"):
            return
        self._ledger.remove_by_id(tid)
        self._store.save_ledger(self._ledger)
        self._refresh_filter_dropdowns()
        self._refresh_table()

    def _on_delete_all(self) -> None:                                                               #Delete all transactions after confirmation
        if len(self._ledger) == 0:
            messagebox.showinfo("No Records", "There are no transactions to delete.")
            return
        if not messagebox.askyesno("Confirm Delete All", "Delete ALL transactions?"):
            return
        self._ledger.clear()
        self._store.save_ledger(self._ledger)
        self._refresh_filter_dropdowns()
        self._refresh_table()

    def _on_set_budget(self) -> None:                                                               #Set or update a budget limit for the selected category
        category = self._var_budget_category.get().strip()
        if not category:
            messagebox.showinfo(
                "Select Category",
                "Please choose an expense category from the Category dropdown.",
            )
            return
        prompt_category = (
            "ALL monthly expenses (excluding Salary)"
            if category == "ALL"
            else f"'{category}'"
        )
        amount_str = simpledialog.askstring(
            "Set Budget", f"Monthly limit for {prompt_category} (HKD):", parent=self
        )
        if amount_str is None:
            return
        try:
            amount = float(amount_str)
            self._budget_book.set_limit(category, amount)
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            return
        self._store.save_budgets(self._budget_book)
        self._refresh_table()

    def _on_remove_budget(self) -> None:                                                             #Remove a budget limit for the selected category
        limits = self._budget_book.all_limits()
        if not limits:
            messagebox.showinfo("No Budgets", "No budget limits are set.")
            return
        category = self._var_budget_category.get().strip()
        if not category:
            messagebox.showinfo(
                "Select Category",
                "Please choose a category from the Category dropdown to remove.",
            )
            return
        removed = self._budget_book.remove_limit(category)
        if removed:
            self._store.save_budgets(self._budget_book)
            self._refresh_filter_dropdowns()
            self._refresh_table()
        else:
            messagebox.showinfo("Not Found", f"No budget limit found for '{category}'.")

    def _clear_filters(self) -> None:                                                               #Clear all filters and show all transactions
        self._var_filter_month.set("")
        self._var_filter_cat.set("ALL")
        self._var_filter_kind.set("All")
        self._refresh_table()


    def _refresh_filter_dropdowns(self) -> None:                                                      #Update month and category dropdown options based on current ledger data
        months = [""] + self._ledger.months()
        self._month_cb["values"] = months

        categories = self._ledger.categories()
        filter_categories = ["ALL"] + categories
        current_filter_category = self._var_filter_cat.get().strip()
        self._filter_cat_cb["values"] = filter_categories
        if not current_filter_category or current_filter_category not in filter_categories:
            self._var_filter_cat.set("ALL")

        expense_categories = sorted(
            {
                t.get_category()
                for t in self._ledger.filter(kind=KIND_EXPENSE)
            }
        )
        budget_limit_categories = sorted(self._budget_book.all_limits().keys())
        budget_categories = ["ALL"] + sorted(
            set(expense_categories).union(budget_limit_categories)
        )
        current_budget_category = self._var_budget_category.get().strip()
        self._budget_cat_cb["values"] = budget_categories
        if current_budget_category not in budget_categories:
            self._var_budget_category.set("ALL")

    def _get_filter_values(self) -> tuple[Optional[str], Optional[str], Optional[str]]:                   #Get current filter values for month, category, and kind to apply to the ledger filtering
        month = self._var_filter_month.get().strip() or None
        category = self._var_filter_cat.get().strip()
        category = None if category == "ALL" else (category or None)
        kind = self._var_filter_kind.get().strip()
        kind = None if kind == "All" else kind
        return month, category, kind

    def _refresh_table(self) -> None:                                                                      #Refresh the transaction table based on current filters
        month, category, kind = self._get_filter_values()
        transactions = self._ledger.filter(month=month, category=category, kind=kind)

        for row in self._tree.get_children():                                                              #Clear table
            self._tree.delete(row)
        self._row_to_tid.clear()

        for t in transactions:
            tag = "expense" if t.get_kind() == KIND_EXPENSE else "income"
            row_id = self._tree.insert(
                "",
                "end",
                values=(
                    t.get_id(),
                    t.get_date(),
                    t.get_kind(),
                    t.get_category(),
                    f"{t.get_amount():,.2f}",
                    t.get_note(),
                ),
                tags=(tag,),
            )
            self._row_to_tid[row_id] = t.get_id()

        self._refresh_summary(transactions)
        self._refresh_budget(month)

    def _refresh_summary(self, transactions: List[Transaction]) -> None:                                  #Refresh the summary panel with total income, expense, net balance, and expense by category based on the currently filtered transactions
        income, expense, net = self._ledger.totals(transactions)
        self._lbl_income.config(text=f"Total Income:  HKD {income:,.2f}")
        self._lbl_expense.config(text=f"Total Expense: HKD {expense:,.2f}")
        self._lbl_net.config(
            text=f"Net Balance:   HKD {net:,.2f}",
            foreground="#27ae60" if net >= 0 else "#c0392b",
        )

        by_cat = self._ledger.by_category(transactions)
        self._cat_list.config(state="normal")
        self._cat_list.delete("1.0", "end")
        if by_cat:
            for cat, total in sorted(by_cat.items(), key=lambda x: -x[1]):
                self._cat_list.insert("end", f"  {cat}: HKD {total:,.2f}\n")
        else:
            self._cat_list.insert("end", "  (no expenses)\n")
        self._cat_list.config(state="disabled")

    def _refresh_budget(self, month: Optional[str]) -> None:                                            #Refresh budget function
        self._budget_text.config(state="normal")
        self._budget_text.delete("1.0", "end")

        if not month:
            self._budget_text.insert("end", "Select a month filter to see budget status.\n", "nomonth")
            limits = self._budget_book.all_limits()
            if limits:
                self._budget_text.insert("end", "\nConfigured limits:\n", "nomonth")
                for cat, lim in sorted(limits.items()):
                    self._budget_text.insert("end", f"  {cat}: HKD {lim:,.2f}\n", "nomonth")
        else:
            warnings = self._budget_book.check_over_budget(self._ledger, month)
            over_cats = {w[0] for w in warnings}
            limits = self._budget_book.all_limits()

            if not limits:
                self._budget_text.insert("end", "No budget limits set.\n", "nomonth")
            else:
                for cat, lim in sorted(limits.items()):
                    spent = self._budget_book.spending_for_month(self._ledger, month, cat)
                    line = f"  {cat}: spent HKD {spent:,.2f} / limit HKD {lim:,.2f}"
                    if cat in over_cats:
                        self._budget_text.insert("end", line + "  ⚠ OVER BUDGET\n", "over")
                    else:
                        self._budget_text.insert("end", line + "  ✓\n", "ok")

        self._budget_text.config(state="disabled")
