from datetime import date
from decimal import Decimal

from expense_tracker import Category, ExpenseError, ExpenseTracker


def print_expenses(expenses):
    if not expenses:
        print("No expenses found.")
        return

    print(f"{'ID':<5}{'Date':<13}{'Category':<17}{'Description':<25}{'Amount':>12}")
    print("-" * 72)
    for expense in expenses:
        print(
            f"{expense.id:<5}{expense.date.isoformat():<13}"
            f"{expense.category.value:<17}{expense.description:<25}"
            f"{expense.amount:>12.2f}"
        )


def print_monthly_report(tracker, year, month):
    report = tracker.monthly_report(year, month)
    print(f"\\nExpense report: {year}-{month:02d}")
    print(f"Total spent: ₹{report['total']:.2f}")

    if report["top_category"] is None:
        print("No expenses recorded for this month.")
        return

    print(f"Top category: {report['top_category'].value}")
    print("\\nCategory breakdown:")
    for category, amount in sorted(
        report["category_totals"].items(), key=lambda item: item[1], reverse=True
    ):
        share = report["shares"][category]
        print(f"  {category.value:<17} ₹{amount:>10.2f}  ({share:.1f}%)")



def main():
    tracker = ExpenseTracker()

    while True:
        print("\n===== EXPENSE TRACKER =====")
        print("1. Add expense")
        print("2. Delete expense")
        print("3. List all expenses")
        print("4. Filter by month")
        print("5. Filter by category")
        print("6. Monthly report")
        print("7. Export expenses to CSV")
        print("8. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                expense_date = input("Date (YYYY-MM-DD): ").strip()
                print("Categories:", ", ".join(
                    category.value for category in Category
                ))
                category = input("Category: ").strip()
                description = input("Description: ").strip()
                amount = input("Amount: ").strip()

                expense = tracker.add(
                    expense_date, category, description, amount
                )
                print(f"Added expense with ID {expense.id}.")

            elif choice == "2":
                expense_id = int(input("Expense ID to delete: "))
                deleted = tracker.delete(expense_id)
                print(f"Deleted: {deleted.description}")

            elif choice == "3":
                print_expenses(tracker.list_expenses())

            elif choice == "4":
                year = int(input("Year: "))
                month = int(input("Month (1-12): "))
                print_expenses(tracker.filter_by_month(year, month))

            elif choice == "5":
                category = input("Category: ").strip()
                print_expenses(tracker.filter_by_category(category))

            elif choice == "6":
                year = int(input("Year: "))
                month = int(input("Month (1-12): "))
                print_monthly_report(tracker, year, month)

            elif choice == "7":
                output_path = input(
                    "CSV filename (default: expenses.csv): "
                ).strip() or "expenses.csv"

                tracker.export_csv(output_path)
                print(f"Expenses exported successfully to {output_path}")

            elif choice == "8":
                print("Goodbye!")
                break

            else:
                print("Please choose a number from 1 to 8.")

        except (ExpenseError, ValueError, OSError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
