import json
from pathlib import Path

import streamlit as st
from charts import (
    grouped_bar_chart,
    pie_chart_inflow,
    pie_chart_outflow,
    stacked_bar_chart_inflow,
    stacked_bar_chart_outflow,
    waterfall_chart,
)
from models import QuarterlyInputData
from reports import ReportFactory

USER_CONFIG = json.load(open("config.json", "r"))

TITLE = f"Quarterly Financial Report - {USER_CONFIG['year']} {USER_CONFIG['quarter']}"
DEFAULT_DECIMALS: int = 2


# ---- MAINPAGE ----
st.set_page_config(page_title=TITLE, page_icon=":bar_chart:", layout="wide")
st.title(f":bar_chart: {TITLE}")


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# ---- READ EXCEL ----
@st.cache_data
def get_report_factory():
    TEST_PATH = Path(USER_CONFIG["path_to_data"])
    result = ReportFactory(TEST_PATH)
    QuarterlyInputData.validate(result.master_raw_data)
    return result


rp_fac = get_report_factory()

# ---- CONTENT ----

st.markdown("""---""")
st.markdown("## 1. Profit & Loss")
result_col, outflow_col, inflow_col = st.columns([0.2, 0.4, 0.4])

pnl = rp_fac.profit_n_loss()
result_col.metric(
    "Monthly Result",
    f"{pnl.profit_n_loss:,.2f} €",
    delta="- Net Loss" if pnl.profit_n_loss < 0 else "+ Net Profit",
)

inflow_col.metric("Inflows", f"{pnl.total_income:,.2f} €")
inflow_col.divider()
in_fix_col, in_var_col = inflow_col.columns(2)
in_fix_col.metric("Fix", f"{pnl.income_fix:,.2f} €")
in_var_col.metric("Variable", f"{pnl.income_var:,.2f} €")

outflow_col.metric("Outflows", f"({pnl.total_expense:,.2f} €)")
outflow_col.divider()
out_fix_col, out_var_col = outflow_col.columns(2)
out_fix_col.metric("Fix", f"({pnl.expense_fix:,.2f} €)")
out_var_col.metric("Var", f"({pnl.expense_var:,.2f} €)")

# ---
st.markdown("""---""")
st.markdown("## 2. In- and Outflow")

left_column_flow, right_column_flow = st.columns(2)

left_column_flow.plotly_chart(
    grouped_bar_chart(rp_fac.income_vs_expense()), use_container_width=True
)
right_column_flow.plotly_chart(
    waterfall_chart(rp_fac.cumulated_overflow_by_month()), use_container_width=True
)

# ---
st.markdown("""---""")
st.markdown("## 3. Fix vs. Var")

left_column_fixvar, right_column_fixvar = st.columns(2)

left_column_fixvar.plotly_chart(
    stacked_bar_chart_outflow(rp_fac.outflow_fix_vs_var()), use_container_width=True
)
right_column_fixvar.plotly_chart(
    stacked_bar_chart_inflow(rp_fac.inflow_fix_vs_var()), use_container_width=True
)


# ---
st.markdown("""---""")
st.markdown("## 4. Categories")

left_column_cat, right_column_cat = st.columns(2)

left_column_cat.plotly_chart(
    pie_chart_outflow(rp_fac.outflow_by_category()), use_container_width=True
)
right_column_cat.plotly_chart(
    pie_chart_inflow(rp_fac.inflow_by_category()), use_container_width=True
)


# ---
st.markdown("""---""")
st.markdown("## 5. Biggest Flows")

st.dataframe(
    rp_fac.show_biggest_expenses(),
    column_config={
        "Betrag": st.column_config.NumberColumn("Betrag", format="%d €"),
        "Buchungstag": st.column_config.DateColumn("Buchungstag", format="YYYY-MM-DD"),
    },
    use_container_width=True,
    hide_index=True,
)

# NOTES --------
# ---
st.markdown("""---""")
st.markdown("## Additional Notes & Remarks")

with st.expander("Notes"):
    st.write(USER_CONFIG["notes"])
