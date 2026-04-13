from __future__ import annotations

from typing import List, Optional

from models.transaction import Transaction, KIND_INCOME, KIND_EXPENSE


class Ledger:                                                                       #ADT for storing and querying transactions

    def __init__(self) -> None:                                                     #Init Function
        self._transactions: List[Transaction] = []
        self._next_id: int = 1

    def _reindex_ids(self) -> None:                                                 #Reassign record IDs starting from 1 after deletions to maintain list consistency
        self._transactions = [
            Transaction(
                date=t.get_date(),
                kind=t.get_kind(),
                category=t.get_category(),
                amount=t.get_amount(),
                note=t.get_note(),
                tid=index,
            )
            for index, t in enumerate(self._transactions, start=1)
        ]
        self._next_id = len(self._transactions) + 1


    def add(self, transaction: Transaction) -> Transaction:                       #Add transaction record Function
        stored = Transaction(
            date=transaction.get_date(),
            kind=transaction.get_kind(),
            category=transaction.get_category(),
            amount=transaction.get_amount(),
            note=transaction.get_note(),
            tid=self._next_id,
        )
        self._transactions.append(stored)
        self._next_id += 1
        return stored

    def remove_by_id(self, tid: int) -> bool:                           #Remove transaction by ID, return True if found
        for i, t in enumerate(self._transactions):
            if t.get_id() == tid:
                del self._transactions[i]
                self._reindex_ids()
                return True
        return False

    def clear(self) -> None:                                            #Clear all transaction records and reset ID counter
        self._transactions.clear()
        self._next_id = 1


    def all(self) -> List[Transaction]:
        return sorted(self._transactions, key=lambda t: t.get_date())

    def filter(                                                          #Filter transactions by month, category, and kind(income/expense)                                          
        self,
        month: Optional[str] = None,
        category: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> List[Transaction]:

        result = self._transactions
        if month:
            result = [t for t in result if t.get_month() == month]
        if category:
            result = [t for t in result if t.get_category() == category]
        if kind and kind.upper() in (KIND_INCOME, KIND_EXPENSE):
            result = [t for t in result if t.get_kind() == kind.upper()]
        return sorted(result, key=lambda t: t.get_date())

    def totals(                                                         #Total function to compute total income, expense, and net balance for a given list of transactions
        self, transactions: Optional[List[Transaction]] = None
    ) -> tuple[float, float, float]:

        subset = transactions if transactions is not None else self._transactions
        income = sum(t.get_amount() for t in subset if t.get_kind() == KIND_INCOME)
        expense = sum(t.get_amount() for t in subset if t.get_kind() == KIND_EXPENSE)
        return income, expense, income - expense


    def by_category(                                                    #Filter by category function to compute total amount spent per category for a given list of transactions
        self, transactions: Optional[List[Transaction]] = None
    ) -> dict[str, float]:

        subset = transactions if transactions is not None else self._transactions
        result: dict[str, float] = {}
        for t in subset:
            if t.get_kind() == KIND_EXPENSE:
                result[t.get_category()] = result.get(t.get_category(), 0.0) + t.get_amount()
        return result

    def categories(self) -> List[str]:                                #Return sorted category strings across all transactions                      
  
        return sorted({t.get_category() for t in self._transactions})

    def months(self) -> List[str]:                                    #Return sorted month strings across all transactions
        return sorted({t.get_month() for t in self._transactions})

    def __len__(self) -> int:
        return len(self._transactions)
