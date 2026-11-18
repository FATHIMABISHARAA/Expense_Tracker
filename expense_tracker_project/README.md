# Python Expense Tracker

A command-line expense tracker built with Python dataclasses, Enum, Decimal, JSON persistence, custom exceptions, and unit tests.

## Requirements

- Python 3.10 or newer
- No third-party packages required

## Run

Open a terminal in this folder and run:

```powershell
python main.py
```

The program creates `expenses.json` automatically when the first expense is saved. The JSON file keeps expense records between runs.

## Run tests

```powershell
python -m unittest -v
```

## Categories

Food, Transport, Shopping, Bills, Health, Education, Entertainment, Other.

## Features

- Add expenses with positive Decimal amounts and valid dates/categories.
- Delete an expense by ID.
- List all expenses.
- Filter by month or category.
- Calculate monthly totals per category.
- Show the month's total, highest-spending category, and category percentages.
- Save and reload records using JSON.

## Example input

- Date: `2026-11-17`
- Category: `Food`
- Description: `Lunch`
- Amount: `250.50`

Amounts are stored as decimal strings in JSON to avoid floating-point rounding issues.
