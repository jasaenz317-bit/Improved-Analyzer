import argparse
from pathlib import Path
from .transactions import load_transactions
from .reports import summarize
from .transactions import to_dataframe
from .db import init_db, insert_transaction


def main():
    parser = argparse.ArgumentParser(description='Personal Finance Analyzer')
    parser.add_argument('--file', '-f', default='data/transactions.csv', help='CSV file with transactions')
    parser.add_argument('--db', help='SQLite DB path to load/save transactions')
    parser.add_argument('--reload', action='store_true', help='Reload transactions into pandas DataFrame')
    parser.add_argument('--plot', choices=['monthly', 'category', 'savings'], help='Create plot: monthly|category|savings')
    parser.add_argument('--plot-month', help='Month (YYYY-MM) for category plot')
    parser.add_argument('--out', help='Output file path to save plot (PNG). If omitted, show interactively')
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}")
        return

    txs = load_transactions(path)
    summary = summarize(txs)

    print(f"Transactions: {summary['count']}")
    print(f"Total: {summary['total']}")
    print("By category:")
    for cat, amt in summary['by_category'].items():
        print(f"  {cat}: {amt}")

    if args.db:
        db_path = Path(args.db)
        init_db(db_path)
        for t in txs:
            insert_transaction(db_path, t)
        print(f"Loaded {len(txs)} transactions into DB: {db_path}")

    if args.reload:
        df = to_dataframe(txs)
        print("Data reloaded into pandas DataFrame:")
        print(df.head().to_string(index=False))

    if args.plot:
        from .viz import plot_monthly_income_expenses, plot_category_pie, plot_savings_trend
        fig = None
        if args.plot == 'monthly':
            fig = plot_monthly_income_expenses(txs)
        elif args.plot == 'category':
            fig = plot_category_pie(txs, month=args.plot_month)
        elif args.plot == 'savings':
            fig = plot_savings_trend(txs)

        if fig is not None:
            if args.out:
                fig.savefig(args.out, bbox_inches='tight')
                print(f"Plot saved to {args.out}")
            else:
                import matplotlib.pyplot as plt
                plt.show()


if __name__ == '__main__':
    main()
