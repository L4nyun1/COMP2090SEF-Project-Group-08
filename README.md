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

# User Guide
## Run main.py to start up the application
## First start up will create data folder automatically for data storage

## How To Use
- A) Add Transation part:
  - 1.Input Date of transaction in 'Date' box, with format in (YYYY-MM-DD), wrong format will result in error and retry is needed.
  - 2.Choose Kind (Income / Expense) by clicking the dropdown menu.
  - 3.Choose Category (Salary, Rent etc) by clicking the dropdown menu.
  - 4.Input the amount of transaction (HKD), non-number will result in error.
  - 5.Enter Note (Remarks if needed, leave blank if not needed).
  - 6. Press ADD button, transaction recrd will be shown in the box below.

- B) Add Filters:
  - 1.Choose the prefered month by clicking the dropdown menu (Only months with transaction record can be chosen)
  - 2.Select category by clicking the dropdown menu ( 'ALL' if all categories are desired).
  - 3.Select kind by clicking the dropdown menu ( 'ALL' if all kinds are desired).
  - 4. Press Clear Filters button if reset is needed.

- C) Delete Records:
  - 1.Click on the disired to be deleted, press Delete Selected button to remove record.
  - 2.Click Delete All if all records needed to be removed.

- D) Summary:
  - 1. Net balance is shown with Income - Expenese.
  - 2. Expense by category is shown in the bottom left box.

- E) Budget Set:
  - 1. Choose Category by clicking the dropdown menu ( All if total budget is disired).
  - 2. Click on Set Budget Limit button.
  - 3. Input the amount ( Non-numbers are not excepted).
  - 4. Budget status according to categories will be shown in the bottom right box.
- F) Budget Removal:
  - 1. Choose Category by clicking the dropdown menu ( All if total budget is disired).
  - 2. Click on Remove Limit button, budget limits will be cleared.
