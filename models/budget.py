from __future__ import annotations

from typing import Dict, List, Tuple, Optional

from models.ledger import Ledger
from models.transaction import KIND_EXPENSE


class BudgetBook:

    def __init__(self) -> None:      #Init Fuction
        self._limits: Dict[str, float] = {}

    @staticmethod
    def _is_salary_category(category: str) -> bool:
        return str(category).strip().upper() == "SALARY"
################################################################################
    def _compute_monthly_spending(self, ledger: Ledger, month: str, category: str) -> float:  #Returns the total amount spent in a given month for a specific category, excluding salary transactions.
 
        filtered = ledger.filter(month=month, kind=KIND_EXPENSE)
        if category == "ALL":
            return sum(
                t.get_amount()
                for t in filtered
                if not self._is_salary_category(t.get_category())
            )
        spent_by_cat = ledger.by_category(transactions=filtered)
        return spent_by_cat.get(category, 0.0)

   ################################################################################

    def set_limit(self, category: str, amount: float) -> None:                               #Set/Update Limit Function
        category = str(category).strip()
        if not category:
            raise ValueError("Category must not be empty.")
        amount = float(amount)
        if amount < 0:
            raise ValueError("Budget limit must be non-negative.")
        self._limits[category] = amount

     ################################################################################
    def remove_limit(self, category: str) -> bool:                                          #Remove Limit Function
        return self._limits.pop(category, None) is not None

    ################################################################################

    def get_limit(self, category: str) -> Optional[float]:                                  #Get Limit Function
        return self._limits.get(category)

     ################################################################################

    def all_limits(self) -> Dict[str, float]:                                               #'ALL' Limits Function
        return dict(self._limits)

    #################################################################################
    def check_over_budget(                                                                  #Check over Budget Function
        self, ledger: Ledger, month: str
    ) -> List[Tuple[str, float, float]]:

        warnings = []                                                                       #Chech each category's spending and return warnings for over-budget categories
        for category, limit in self._limits.items():
            spent = self._compute_monthly_spending(ledger, month, category)
            if spent > limit:
                warnings.append((category, spent, limit))
        return warnings

    def spending_for_month(self, ledger: Ledger, month: str, category: str) -> float:
        return self._compute_monthly_spending(ledger, month, category)

    ################################################################################

    def to_dict(self) -> dict:
        return dict(self._limits)

    @classmethod

    def from_dict(cls, data: dict) -> "BudgetBook":
        book = cls()
        for category, amount in data.items():
            book.set_limit(category, amount)
        return book


    def __len__(self) -> int:                                   
        return len(self._limits)
