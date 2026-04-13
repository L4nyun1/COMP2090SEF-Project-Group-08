from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.ledger import Ledger
    from models.budget import BudgetBook


class JsonStore:                                                            #ADT for persisting Ledger and BudgetBook data to JSON files

    def __init__(self, ledger_path: str, budgets_path: str) -> None:        #Init Function
        self._ledger_path = ledger_path
        self._budgets_path = budgets_path


    def save_ledger(self, ledger: "Ledger") -> None:                        #Ledger persistence using save_ledgar function
        self._ensure_dir(self._ledger_path)
        data = [t.to_dict() for t in ledger.all()]
        with open(self._ledger_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    def load_ledger(self) -> "Ledger":                                      #Load data from JSON files
        from models.ledger import Ledger
        from models.transaction import Transaction

        ledger = Ledger()
        if not os.path.exists(self._ledger_path):
            return ledger
        with open(self._ledger_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for item in data:
            ledger.add(Transaction.from_dict(item))
        return ledger

    def save_budgets(self, budget_book: "BudgetBook") -> None:              #Save budget limits to JSON files
        self._ensure_dir(self._budgets_path)
        with open(self._budgets_path, "w", encoding="utf-8") as fh:
            json.dump(budget_book.to_dict(), fh, ensure_ascii=False, indent=2)

    def load_budgets(self) -> "BudgetBook":                                 #Load budget limits from JSON files
        from models.budget import BudgetBook

        if not os.path.exists(self._budgets_path):
            return BudgetBook()
        with open(self._budgets_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return BudgetBook.from_dict(data)

    @staticmethod                                                           
    def _ensure_dir(path: str) -> None:                                     #Confirm directory exists for a given file path, creating it if necessary
        directory = os.path.dirname(path)                                   #Prevent error when saving to non-existent directories
        if directory:
            os.makedirs(directory, exist_ok=True)                           #Create directory if it doesnt exist
