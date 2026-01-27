import streamlit as st
from pathlib import Path
import tempfile
import io
import sys

# Ensure project root is on sys.path so `src` package imports work when running via Streamlit
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.transactions import load_transactions, to_dataframe
from src.reports import monthly_metrics, monthly_category_breakdown
from src.viz import plot_monthly_income_expenses, plot_category_pie, plot_savings_trend

st.set_page_config(page_title='Personal Finance Analyzer', layout='wide')

st.title('Personal Finance Analyzer')

sidebar = st.sidebar
sidebar.header('Data')
use_sample = sidebar.checkbox('Use sample data (data/transactions.csv)', value=True)
uploaded = sidebar.file_uploader('Or upload transactions CSV', type=['csv'])

normalize = sidebar.selectbox('Normalize dates', options=['None', 'start', 'end'])
plot_choice = sidebar.selectbox('Plot', options=['Monthly Income vs Expenses', 'Category Spending', 'Savings Trend'])
plot_month = sidebar.text_input('Plot month (YYYY-MM) for category chart', value='')

# Load file
if uploaded is not None:
    tf = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    tf.write(uploaded.getvalue())
    tf.flush()
    tf.close()
    data_path = Path(tf.name)
elif use_sample:
    data_path = Path('data/transactions.csv')
else:
    st.warning('Please upload a CSV or enable sample data.')
    st.stop()

try:
    transactions = load_transactions(data_path)
except Exception as e:
    st.error(f'Failed to load transactions: {e}')
    st.stop()

# DataFrame
norm_arg = None if normalize == 'None' else normalize
df = to_dataframe(transactions, normalize=norm_arg)

with st.expander('Raw data'):
    st.dataframe(df)

# Metrics
metrics = monthly_metrics(transactions)

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader('Monthly Metrics')
    # Convert to table
    import pandas as pd
    rows = []
    for m in sorted(metrics.keys()):
        r = metrics[m]
        rows.append({
            'month': m,
            'income': float(r['income']),
            'expenses': float(r['expenses']),
            'net': float(r['net']),
            'savings_rate': float(r['savings_rate']) if r['savings_rate'] is not None else None,
        })
    st.table(pd.DataFrame(rows))

with col2:
    st.subheader('Category Breakdown (selected month)')
    breakdown = monthly_category_breakdown(transactions, expenses_only=True)
    if plot_month and plot_month in breakdown:
        st.table(breakdown[plot_month]['amounts'])
    else:
        # show top categories overall
        from src.reports import category_percentages
        pct = category_percentages(transactions, expenses_only=True)
        st.table(pct)

# Plots
st.subheader('Visualizations')
fig = None
if plot_choice == 'Monthly Income vs Expenses':
    fig = plot_monthly_income_expenses(transactions)
elif plot_choice == 'Category Spending':
    month_arg = plot_month if plot_month else None
    fig = plot_category_pie(transactions, month=month_arg)
elif plot_choice == 'Savings Trend':
    fig = plot_savings_trend(transactions)

if fig is not None:
    st.pyplot(fig)
    # download button
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    st.download_button('Download plot PNG', data=buf, file_name='plot.png', mime='image/png')
