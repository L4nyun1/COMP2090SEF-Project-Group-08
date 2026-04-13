from __future__ import annotations

import re
from datetime import date as _date_type

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

KIND_INCOME = "INCOME"
KIND_EXPENSE = "EXPENSE"
VALID_KINDS = (KIND_INCOME, KIND_EXPENSE)


class Transaction:                                              #ADT for financial transactions
    def __init__(                                               #Init Function
        self,
        date: str,
        kind: str,
        category: str,
        amount: float,
        note: str = "",
        tid: int | None = None,
    ) -> None:
        self._tid: int | None = tid
        self._date: str = self._validate_date(date)
        self._kind: str = self._validate_kind(kind)
        self._category: str = self._validate_category(category)
        self._amount: float = self._validate_amount(amount)
        self._note: str = str(note)

    @staticmethod
    def _validate_date(value: str) -> str:                     #Check date string is in YYYY-MM-DD format 
        value = str(value).strip()
        if not _DATE_RE.match(value):
            raise ValueError(f"Date must be YYYY-MM-DD, got: {value!r}")
        try:
            _date_type.fromisoformat(value)
        except ValueError:
            raise ValueError(f"Invalid calendar date: {value!r}")
        return value

    @staticmethod
    def _validate_kind(value: str) -> str:                   #Check kind string is either INCOME or EXPENSE                             
        value = str(value).strip().upper()
        if value not in VALID_KINDS:
            raise ValueError(f"Kind must be INCOME or EXPENSE, got: {value!r}")
        return value

    @staticmethod
    def _validate_category(value: str) -> str:              #Check category string is non-empty after stripping whitespace
        value = str(value).strip()
        if not value:
            raise ValueError("Category must not be empty.")
        return value

    @staticmethod
    def _validate_amount(value: float) -> float:            #Check amount is a positive number
        try:
            amount = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Amount must be a number, got: {value!r}")
        if amount <= 0:
            raise ValueError(f"Amount must be positive, got: {amount}")
        return amount

    def get_id(self) -> int | None:                          #Get  ID Function
        return self._tid

    def get_date(self) -> str:                               #Get date Function  
        return self._date

    def get_kind(self) -> str:                               #Get kind Function
        return self._kind

    def get_category(self) -> str:                           #Get category Function
        return self._category

    def get_amount(self) -> float:                           #Get amount Function
        return self._amount

    def get_note(self) -> str:                               #Get note Function
        return self._note

    def get_month(self) -> str:                              #Get month Function
        """Return the YYYY-MM portion of the date."""
        return self._date[:7]

    def signed_amount(self) -> float:                       #Signed amount Function
        """Return +amount for income, -amount for expense."""
        return self._amount if self._kind == KIND_INCOME else -self._amount


    def to_dict(self) -> dict:                              #Convert transactions to a dictionary for serialization
        return {
            "tid": self._tid,
            "date": self._date,
            "kind": self._kind,
            "category": self._category,
            "amount": self._amount,
            "note": self._note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":         #Create a Transaction from a dictionary, Checking fields in the process
        return cls(
            date=data["date"],
            kind=data["kind"],
            category=data["category"],
            amount=data["amount"],
            note=data.get("note", ""),
            tid=data.get("tid"),
        )

    def __repr__(self) -> str:                              #String representation of a Transaction for debugging purposes
        return (
            f"Transaction(tid={self._tid}, date={self._date!r}, "
            f"kind={self._kind!r}, category={self._category!r}, "
            f"amount={self._amount:.2f})"
        )
