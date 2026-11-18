
import tempfile
import unittest
import csv

from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker import Category, ExpenseError, ExpenseTracker


class ExpenseTrackerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "expenses.json"
        self.tracker = ExpenseTracker(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_persistence(self):
        added = self.tracker.add(
            "2026-11-17", "Food", "Lunch", "125.50"
        )
        self.assertEqual(added.id, 1)

        reloaded = ExpenseTracker(self.file_path)

        self.assertEqual(len(reloaded.list_expenses()), 1)
        self.assertEqual(
            reloaded.list_expenses()[0].amount,
            Decimal("125.50")
        )

    def test_reject_invalid_amount(self):
        with self.assertRaises(ExpenseError):
            self.tracker.add(
                date(2026, 11, 17), Category.FOOD, "Lunch", 0
            )

    def test_reject_unknown_category(self):
        with self.assertRaises(ExpenseError):
            self.tracker.add(
                "2026-11-17", "Travel", "Taxi", 100
            )

    def test_delete(self):
        self.tracker.add("2026-11-17", "Food", "Lunch", 100)
        self.tracker.delete(1)

        self.assertEqual(self.tracker.list_expenses(), [])

    def test_monthly_report(self):
        self.tracker.add("2026-11-01", "Food", "Groceries", 300)
        self.tracker.add("2026-11-02", "Transport", "Bus", 100)

        report = self.tracker.monthly_report(2026, 11)

        self.assertEqual(report["total"], Decimal("400"))
        self.assertEqual(report["top_category"], Category.FOOD)
        self.assertEqual(report["shares"][Category.FOOD], Decimal("75"))

    def test_empty_month_report(self):
        report = self.tracker.monthly_report(2026, 1)

        self.assertEqual(report["total"], Decimal("0.00"))
        self.assertIsNone(report["top_category"])
        self.assertEqual(report["shares"], {})

    # NEW TESTS FOR MONTHLY SUMMARY

    def test_monthly_summary_total(self):
        self.tracker.add("2026-11-01", "Food", "Lunch", 300)
        self.tracker.add("2026-11-02", "Transport", "Bus", 100)

        summary = self.tracker.monthly_summary(2026, 11)

        self.assertEqual(summary["total"], Decimal("400"))

    def test_monthly_summary_top_category(self):
        self.tracker.add("2026-11-01", "Food", "Lunch", 300)
        self.tracker.add("2026-11-02", "Transport", "Bus", 100)

        summary = self.tracker.monthly_summary(2026, 11)

        self.assertEqual(summary["top_category"], Category.FOOD)

    def test_monthly_summary_category_totals(self):
        self.tracker.add("2026-11-01", "Food", "Lunch", 300)
        self.tracker.add("2026-11-02", "Food", "Dinner", 200)
        self.tracker.add("2026-11-03", "Transport", "Bus", 100)

        summary = self.tracker.monthly_summary(2026, 11)

        self.assertEqual(
            summary["category_totals"][Category.FOOD],
            Decimal("500")
        )
        self.assertEqual(
            summary["category_totals"][Category.TRANSPORT],
            Decimal("100")
        )

    def test_monthly_summary_shares(self):
        self.tracker.add("2026-11-01", "Food", "Lunch", 300)
        self.tracker.add("2026-11-02", "Transport", "Bus", 100)

        summary = self.tracker.monthly_summary(2026, 11)

        self.assertEqual(
            summary["shares"][Category.FOOD],
            Decimal("75")
        )
        self.assertEqual(
            summary["shares"][Category.TRANSPORT],
            Decimal("25")
        )

    def test_monthly_summary_empty_month(self):
        summary = self.tracker.monthly_summary(2026, 12)

        self.assertEqual(summary["total"], Decimal("0.00"))
        self.assertIsNone(summary["top_category"])
        self.assertEqual(summary["category_totals"], {})
        self.assertEqual(summary["shares"], {})

    # NEW TEST FOR CSV EXPORT

    def test_csv_export(self):
        self.tracker.add("2026-11-01", "Food", "Lunch", 300)

        csv_path = Path(self.temp_dir.name) / "expenses.csv"

        self.tracker.export_csv(csv_path)

        self.assertTrue(csv_path.exists())

        with csv_path.open(
            "r", newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "Food")
        self.assertEqual(rows[0]["description"], "Lunch")
        self.assertEqual(rows[0]["amount"], "300")

    def test_monthly_summary_excludes_other_months(self):
        self.tracker.add("2026-11-01", "Food", "Lunch", 300)
        self.tracker.add("2026-10-01", "Shopping", "Shoes", 500)

        summary = self.tracker.monthly_summary(2026, 11)

        self.assertEqual(summary["total"], Decimal("300"))


if __name__ == "__main__":
    unittest.main()
