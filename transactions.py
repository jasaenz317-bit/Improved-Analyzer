from dataclasses import dataclass
from decimal import Decimal
from typing import List, Union
from pathlib import Path
import csv
from datetime import date
import pandas as pd


@dataclass
class Transaction:
    date: date
    description: str
    amount: Decimal
    category: str


def load_transactions(path: Union[str, Path]) -> List[Transaction]:
    transactions: List[Transaction] = []
    path = Path(path)
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            amt = Decimal(row.get('amount', '0').strip())
            d = row.get('date', '').strip()
            # Use pandas for flexible date parsing (accepts multiple formats)
            # `infer_datetime_format` is deprecated; remove it to silence warnings.
            parsed_date = pd.to_datetime(d, errors='raise').date()
            transactions.append(
                Transaction(
                    date=parsed_date,
                    description=row.get('description', '').strip(),
                    amount=amt,
                    category=row.get('category', '').strip() or 'Uncategorized',
                )
            )
    return transactions


def to_dataframe(transactions: List[Transaction], normalize: str | None = None) -> pd.DataFrame:
    """Convert a list of Transaction into a pandas DataFrame with proper dtypes.

    normalize: optional; one of `None`, `'start'`, or `'end'`.
      - `'start'` sets each date to the first day of its month.
      - `'end'` sets each date to the last day of its month.
    """
    rows = [
        {
            'date': t.date,
            'description': t.description,
            'amount': t.amount,
            'category': t.category,
        }
        for t in transactions
    ]
    df = pd.DataFrame(rows)
    if not df.empty:
        # Keep `date` as pandas datetime64 for easier resampling/grouping
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = df['amount'].astype('float')

        if normalize is not None:
            norm = normalize.lower()
            if norm == 'start':
                # Convert to period-month then back to timestamp (month start)
                df['date'] = df['date'].dt.to_period('M').dt.to_timestamp()
            elif norm == 'end':
                # Convert to month-end timestamps
                df['date'] = df['date'].dt.to_period('M').dt.to_timestamp(how='end')
            else:
                raise ValueError("normalize must be one of None, 'start', or 'end'")
    return df
