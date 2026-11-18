from __future__ import annotations
import csv
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import Iterable


class ExpenseError(Exception):
    """Raised when expense data is invalid or an expense cannot be found."""


class Category(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    HEALTH = "Health"
    EDUCATION = "Education"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


@dataclass
class Expense:
    id: int
    date: date
    category: Category
    description: str
    amount: Decimal

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "category": self.category.value,
            "description": self.description,
            "amount": str(self.amount),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        try:
            return cls(
                id=int(data["id"]),
                date=date.fromisoformat(data["date"]),
                category=Category(data["category"]),
                description=str(data["description"]),
                amount=Decimal(str(data["amount"])),
            )
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise ExpenseError(f"Invalid expense data in JSON: {exc}") from exc


class ExpenseTracker:
    def __init__(self, file_path: str | Path = "expenses.json"):
        self.file_path = Path(file_path)
        self._expenses: list[Expense] = []
        self.load()

    @staticmethod
    def _validate(expense_date, category, description, amount) -> tuple[date, Category, str, Decimal]:
        if isinstance(expense_date, str):
            try:
                expense_date = date.fromisoformat(expense_date)
            except ValueError as exc:
                raise ExpenseError("Date must be valid and use YYYY-MM-DD format.") from exc
        if not isinstance(expense_date, date):
            raise ExpenseError("Date must be a valid datetime.date value.")

        try:
            category = category if isinstance(category, Category) else Category(category)
        except (ValueError, TypeError) as exc:
            raise ExpenseError(f"Unknown category: {category!r}") from exc

        description = str(description).strip()
        if not description:
            raise ExpenseError("Description cannot be empty.")

        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ExpenseError("Amount must be a valid number.") from exc

        if not amount.is_finite() or amount <= 0:
            raise ExpenseError("Amount must be greater than zero.")

        return expense_date, category, description, amount

    def add(self, expense_date, category, description, amount) -> Expense:
        expense_date, category, description, amount = self._validate(
            expense_date, category, description, amount
        )
        new_id = max((expense.id for expense in self._expenses), default=0) + 1
        expense = Expense(new_id, expense_date, category, description, amount)
        self._expenses.append(expense)
        self.save()
        return expense

    def delete(self, expense_id: int) -> Expense:
        for index, expense in enumerate(self._expenses):
            if expense.id == expense_id:
                deleted = self._expenses.pop(index)
                self.save()
                return deleted
        raise ExpenseError(f"No expense found with id {expense_id}.")

    def list_expenses(self) -> list[Expense]:
        return sorted(self._expenses, key=lambda item: (item.date, item.id))

    def filter_by_month(self, year: int, month: int) -> list[Expense]:
        if not 1 <= month <= 12:
            raise ExpenseError("Month must be between 1 and 12.")
        return [
            expense for expense in self.list_expenses()
            if expense.date.year == year and expense.date.month == month
        ]

    def filter_by_category(self, category: Category | str) -> list[Expense]:
        try:
            category = category if isinstance(category, Category) else Category(category)
        except (ValueError, TypeError) as exc:
            raise ExpenseError(f"Unknown category: {category!r}") from exc
        return [expense for expense in self.list_expenses() if expense.category == category]

    def monthly_totals_by_category(self, year: int, month: int) -> dict[Category, Decimal]:
        totals = {category: Decimal("0.00") for category in Category}
        for expense in self.filter_by_month(year, month):
            totals[expense.category] += expense.amount
        return {category: total for category, total in totals.items() if total > 0}

    def monthly_report(self, year: int, month: int) -> dict:
        expenses = self.filter_by_month(year, month)
        category_totals = self.monthly_totals_by_category(year, month)
        total = sum((expense.amount for expense in expenses), Decimal("0.00"))
        top_category = (
            max(category_totals, key=category_totals.get) if category_totals else None
        )
        shares = {
            category: (amount / total * Decimal("100"))
            for category, amount in category_totals.items()
        } if total else {}

        return {
            "year": year,
            "month": month,
            "total": total,
            "top_category": top_category,
            "category_totals": category_totals,
            "shares": shares,
        }

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
        payload = [expense.to_dict() for expense in self._expenses]
        temporary_path.write_text(json.dumps(payload, indent=4), encoding="utf-8")
        temporary_path.replace(self.file_path)

    def load(self) -> None:
        if not self.file_path.exists():
            self._expenses = []
            return
        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ExpenseError("JSON file must contain a list of expenses.")
            loaded = [Expense.from_dict(item) for item in payload]
            ids = [expense.id for expense in loaded]
            if len(ids) != len(set(ids)):
                raise ExpenseError("JSON file contains duplicate expense IDs.")
            for expense in loaded:
                self._validate(expense.date, expense.category, expense.description, expense.amount)
            self._expenses = loaded
        except (json.JSONDecodeError, OSError) as exc:
            raise ExpenseError(f"Could not load expense file: {exc}") from exc
    def monthly_summary(self, year: int, month: int) -> dict:
        """Return a summary of expenses for a given month."""
        return self.monthly_report(year, month)


    def export_csv(self, output_path: str | Path = "expenses.csv") -> None:
        """Export all expenses to a CSV file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["id", "date", "category", "description", "amount"]
            )

            writer.writeheader()

            for expense in self.list_expenses():
                writer.writerow({
                    "id": expense.id,
                    "date": expense.date.isoformat(),
                    "category": expense.category.value,
                    "description": expense.description,
                    "amount": str(expense.amount),
                })