# Personal Expense Tracker App

## Features

- **Add Transactions** — Record income or expense with date, category, amount, and an optional note.
- **Transaction Table** — View all records in a sortable table, delete selected or all entries.
- **Filters** — Filter by month (YYYY-MM), category, or kind (Income / Expense).
- **Summary Panel** — Sumarize total income, total expense, net balance, and a per-category expense breakdown for the filtered view.
- **Budget Limits** — Set monthly spending limits per category, over-budget categories are highlighted in the selected month.
- **Data Persistence** — All data is saved automatically to `data/ledger.json` and `data/budgets.json`.

## Requirements

- Python 3.10 or newer (Tkinter is included in the standard library)

## Running the App

```bash
python main.py
```

## Project Structure

```
├── main.py                  # Entry point (Main App)
├── models/
│   ├── transaction.py       # Transaction ADT
│   ├── ledger.py            # Ledger ADT
│   └── budget.py            # BudgetBook ADT
├── storage/
│   └── json_store.py        # JSON persistance( for data)
├── ui/
│   └── app.py               # Tkinter GUI class
└── data/                    # Auto-created to stores ledger.json and budgets.json
```

## OOP / ADT Design

| Class | Role |
|---|---|
| `Transaction` | Immutable-like record with private fields and public getters; validates input on construction |
| `Ledger` | Collection ADT — `add()`, `remove_by_id()`, `filter()`, `totals()`, `by_category()` |
| `BudgetBook` | Stores category limits; `check_over_budget()` compares spending against limits |
| `JsonStore` | Utility class that serialises / deserialises Ledger and BudgetBook to JSON files |
| `ExpenseTrackerApp` | Tkinter `Tk` subclass; delegates all data logic to the ADTs above |
