from typing import List, Optional
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.ticker as mtick
import pandas as pd
from .reports import monthly_metrics, monthly_category_breakdown
from .transactions import Transaction
from decimal import Decimal

# Try to use seaborn for nicer default styling, fall back to matplotlib style
try:
    import seaborn as sns
    sns.set_theme(context='talk', style='whitegrid', palette='muted')
    _PALETTE = sns.color_palette()
except Exception:
    plt.style.use('seaborn-v0_8-darkgrid')
    _PALETTE = list(plt.rcParams.get('axes.prop_cycle').by_key().get('color', ['#1f77b4', '#ff7f0e']))


def plot_monthly_income_expenses(transactions: List[Transaction], *, figsize=(10, 6)) -> Figure:
    metrics = monthly_metrics(transactions)
    months = sorted(metrics.keys())
    income = [metrics[m]['income'] for m in months]
    expenses = [metrics[m]['expenses'] for m in months]

    fig, ax = plt.subplots(figsize=figsize)
    x = list(range(len(months)))
    inc_vals = [float(i) for i in income]
    exp_vals = [float(e) for e in expenses]
    income_color = _PALETTE[2 % len(_PALETTE)]
    expense_color = '#d62728' if len(_PALETTE) < 4 else _PALETTE[3 % len(_PALETTE)]
    ax.bar([i - 0.2 for i in x], inc_vals, width=0.4, label='Income', color=income_color)
    ax.bar([i + 0.2 for i in x], exp_vals, width=0.4, label='Expenses', color=expense_color)
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45)
    ax.set_ylabel('Amount')
    ax.set_title('Monthly Income vs Expenses')
    ax.legend()
    # Annotate bars
    for xi, val in zip(x, inc_vals):
        ax.annotate(f"${val:,.0f}", (xi - 0.2, val), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=9)
    for xi, val in zip(x, exp_vals):
        ax.annotate(f"${val:,.0f}", (xi + 0.2, val), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=9)
    fig.tight_layout()
    return fig


def plot_category_pie(transactions: List[Transaction], month: Optional[str] = None, *, expenses_only: bool = True, figsize=(8, 8)) -> Figure:
    # If month provided, compute breakdown for that month, otherwise overall
    if month is not None:
        breakdown = monthly_category_breakdown(transactions, expenses_only=expenses_only)
        data = breakdown.get(month)
        if not data:
            labels = []
            sizes = []
        else:
            labels = list(data['amounts'].keys())
            sizes = [float(v) for v in data['amounts'].values()]
    else:
        # overall
        from .reports import category_percentages
        pct = category_percentages(transactions, expenses_only=expenses_only)
        labels = list(pct.keys())
        sizes = [float(pct[k]) for k in labels]

    fig, ax = plt.subplots(figsize=figsize)
    if sizes:
        # choose colors from palette
        colors = [_PALETTE[i % len(_PALETTE)] for i in range(len(sizes))]
        # explode the largest slice slightly
        if sizes:
            max_idx = int(pd.Series(sizes).idxmax())
            explode = [0.05 if i == max_idx else 0 for i in range(len(sizes))]
        else:
            explode = None
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, explode=explode)
    ax.set_title('Category Spending')
    fig.tight_layout()
    return fig


def plot_savings_trend(transactions: List[Transaction], *, figsize=(10, 6)) -> Figure:
    metrics = monthly_metrics(transactions)
    months = sorted(metrics.keys())
    savings = [metrics[m]['savings_rate'] if metrics[m]['savings_rate'] is not None else Decimal('0') for m in months]
    fig, ax = plt.subplots(figsize=figsize)
    vals = [float(s) for s in savings]
    ax.plot(months, vals, marker='o', color=_PALETTE[0])
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45)
    ax.set_ylim(-1, 1)
    ax.set_ylabel('Savings rate')
    ax.set_title('Savings Rate Over Time')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.grid(True, axis='y', linestyle='--', alpha=0.6)
    fig.tight_layout()
    return fig