from typing import List, Dict, Iterable
from decimal import Decimal, getcontext
from collections import defaultdict
from .transactions import Transaction
from datetime import date


getcontext().prec = 9


def summarize(transactions: List[Transaction]) -> Dict[str, object]:
    total = Decimal('0')
    by_category: Dict[str, Decimal] = {}
    for t in transactions:
        total += t.amount
        by_category.setdefault(t.category, Decimal('0'))
        by_category[t.category] += t.amount
    return {
        'count': len(transactions),
        'total': total,
        'by_category': by_category,
    }


def _group_by_month(transactions: Iterable[Transaction]) -> Dict[str, List[Transaction]]:
    groups: Dict[str, List[Transaction]] = defaultdict(list)
    for t in transactions:
        key = f"{t.date.year:04d}-{t.date.month:02d}"
        groups[key].append(t)
    return groups


def monthly_metrics(transactions: List[Transaction]) -> Dict[str, Dict[str, Decimal]]:
    """Return per-month metrics keyed by 'YYYY-MM'.

    Each month's dict contains:
    - income: sum of positive amounts
    - expenses: sum of absolute values of negative amounts
    - net: income - expenses
    - savings_rate: (income - expenses) / income (Decimal) or None if income == 0
    """
    out: Dict[str, Dict[str, Decimal]] = {}
    groups = _group_by_month(transactions)
    for month, txs in groups.items():
        income = Decimal('0')
        expenses = Decimal('0')
        for t in txs:
            if t.amount >= 0:
                income += t.amount
            else:
                expenses += -t.amount
        net = income - expenses
        savings_rate = None
        if income != 0:
            savings_rate = (net / income).quantize(Decimal('0.0001'))
        out[month] = {
            'income': income,
            'expenses': expenses,
            'net': net,
            'savings_rate': savings_rate,
        }
    return out


def category_percentages(transactions: List[Transaction], *, expenses_only: bool = True) -> Dict[str, Decimal]:
    """Return percentage share per category.

    If `expenses_only` is True, only considers negative amounts (expenses) and
    reports percentage of total expenses for each category. Otherwise all amounts
    are used and shares are relative to the absolute total.
    """
    by_cat: Dict[str, Decimal] = defaultdict(lambda: Decimal('0'))
    total = Decimal('0')
    for t in transactions:
        amt = t.amount
        if expenses_only:
            if amt >= 0:
                continue
            amt = -amt
        else:
            if amt < 0:
                amt = -amt
        by_cat[t.category] += amt
        total += amt

    if total == 0:
        return {k: Decimal('0') for k in by_cat}

    percentages: Dict[str, Decimal] = {}
    for k, v in by_cat.items():
        percentages[k] = (v / total * Decimal('100')).quantize(Decimal('0.01'))
    return percentages


def monthly_category_breakdown(transactions: List[Transaction], *, expenses_only: bool = True) -> Dict[str, Dict[str, Dict[str, Decimal]]]:
    """Return per-month category breakdown.

    Returns a dict keyed by 'YYYY-MM' where each value is a dict with:
      - 'amounts': mapping category -> Decimal(amount)
      - 'percentages': mapping category -> Decimal(percentage of total for that month)

    If `expenses_only` is True, only negative amounts (expenses) are counted.
    """
    groups = _group_by_month(transactions)
    out: Dict[str, Dict[str, Dict[str, Decimal]]] = {}
    for month, txs in groups.items():
        by_cat: Dict[str, Decimal] = defaultdict(lambda: Decimal('0'))
        total = Decimal('0')
        for t in txs:
            amt = t.amount
            if expenses_only:
                if amt >= 0:
                    continue
                amt = -amt
            else:
                if amt < 0:
                    amt = -amt
            by_cat[t.category] += amt
            total += amt

        percentages: Dict[str, Decimal] = {}
        if total == 0:
            for k in by_cat:
                percentages[k] = Decimal('0')
        else:
            for k, v in by_cat.items():
                percentages[k] = (v / total * Decimal('100')).quantize(Decimal('0.01'))

        out[month] = {
            'amounts': dict(by_cat),
            'percentages': percentages,
        }
    return out


def month_to_month_changes(transactions: List[Transaction]) -> Dict[str, Dict[str, Dict[str, Decimal]]]:
    """Compute month-to-month changes for income, expenses, and net.

    Returns dict keyed by month 'YYYY-MM'. For the first month values will be None.
    Each month's value is a dict with keys 'income', 'expenses', 'net' each mapping to
    {'change': Decimal or None, 'pct_change': Decimal or None} where pct_change is in
    decimal fraction (e.g., 0.1 == 10%).
    """
    metrics = monthly_metrics(transactions)
    months = sorted(metrics.keys())
    out: Dict[str, Dict[str, Dict[str, Decimal]]] = {}
    prev = None
    for m in months:
        cur = metrics[m]
        if prev is None:
            out[m] = {
                'income': {'change': None, 'pct_change': None},
                'expenses': {'change': None, 'pct_change': None},
                'net': {'change': None, 'pct_change': None},
            }
        else:
            row = {}
            for key in ('income', 'expenses', 'net'):
                cur_val = cur[key]
                prev_val = prev[key]
                change = (cur_val - prev_val)
                pct = None
                if prev_val != 0:
                    pct = (change / prev_val).quantize(Decimal('0.0001'))
                row[key] = {'change': change, 'pct_change': pct}
            out[m] = row
        prev = cur
    return out
