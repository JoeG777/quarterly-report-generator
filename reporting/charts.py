from dataclasses import asdict
from pathlib import Path

import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
from reports import ReportFactory

OUTFLOW_COLOR_CODE = "#ED7D31"
INFLOW_COLOR_CODE = "#002060"
AXIS_LABEL_DICT = {"prep_Month": "Month", "Betrag": "[in €]"}


def pie_chart_outflow(df: pd.DataFrame):
    fig = px.pie(
        df,
        values="Betrag",
        title="Expenses by Category",
        names=df.index,
        color_discrete_sequence=px.colors.sequential.Oranges[::-1],
    )
    fig.update_traces(textinfo="value", texttemplate="- %{value:.2f} €")
    return fig


def pie_chart_inflow(df: pd.DataFrame):
    fig = px.pie(
        df,
        values="Betrag",
        title="Inflow by Category",
        names=df.index,
        color_discrete_sequence=px.colors.sequential.Blues[::-1],
    )
    fig.update_traces(textinfo="value", texttemplate="%{value:.2f} €")
    return fig


def grouped_bar_chart(df: pd.DataFrame):
    df = df.reset_index()
    df = df[df["prep_Type"] != "Umbuchung"]
    df["Betrag"] = df["Betrag"].abs()

    fig = px.bar(
        df,
        x="prep_Month",
        y="Betrag",
        title="In- vs. Outflow",
        color="prep_Type",
        labels=AXIS_LABEL_DICT,
        text=df["Betrag"].map(lambda x: f"{round(x, 2)} €"),
        barmode="group",
        color_discrete_map={
            "Einnahme": INFLOW_COLOR_CODE,
            "Ausgabe": OUTFLOW_COLOR_CODE,
        },
    )
    fig.update_layout(
        legend=dict(
            title="",
            x=0.8,
            y=1,
        )
    )
    return fig


def waterfall_chart(df: pd.DataFrame):
    df = df.reset_index()
    df["measure"] = "relative"
    df["text"] = df["Betrag"].map(lambda x: f"{round(x, 2)} €")
    fig = go.Figure(
        go.Waterfall(
            measure=df["measure"],
            x=df["prep_Month"],
            textposition="outside",
            text=df["text"],
            y=df["Betrag"],
            decreasing={"marker": {"color": OUTFLOW_COLOR_CODE}},
            increasing={"marker": {"color": INFLOW_COLOR_CODE}},
        )
    )

    fig.update_layout(
        title="Cumulated Overflow", showlegend=False, yaxis=dict(tickformat="€,.2f")
    )
    fig.update_xaxes(title_text=AXIS_LABEL_DICT["prep_Month"])  # Naming the x-axis
    fig.update_yaxes(title_text=AXIS_LABEL_DICT["Betrag"])  # Naming the y-axis

    return fig


def stacked_bar_chart_outflow(df: pd.DataFrame):
    df = df.reset_index()
    df["Betrag"] = df["Betrag"].abs()
    fig = px.bar(
        df,
        x="prep_Month",
        color="prep_Recurring",
        y="Betrag",
        title="Fix vs. Var - Outflow",
        labels=AXIS_LABEL_DICT,
        text=df["Betrag"].map(lambda x: f"- {round(x, 2)} €"),
        color_discrete_sequence=[OUTFLOW_COLOR_CODE, "#F4B183"],
    )
    fig.update_layout(
        legend=dict(
            title="",
            x=0.85,
            y=1,
        )
    )
    return fig


def stacked_bar_chart_inflow(df: pd.DataFrame):
    df = df.reset_index()
    df["Betrag"] = df["Betrag"].abs()
    fig = px.bar(
        df,
        x="prep_Month",
        color="prep_Recurring",
        y="Betrag",
        title="Fix vs. Var - Inflow",
        labels=AXIS_LABEL_DICT,
        text=df["Betrag"].map(lambda x: f"{round(x, 2)} €"),
        color_discrete_sequence=[INFLOW_COLOR_CODE, "#8FAADC"],
    )
    fig.update_layout(
        legend=dict(
            title="",
            x=0.85,
            y=1,
        )
    )
    return fig


def table_pnl(pnl_class):
    fig = go.Figure(
        data=[
            go.Table(
                cells=dict(
                    values=[
                        [key for key in asdict(pnl_class).keys()],
                        [value for value in asdict(pnl_class).values()],
                    ]
                )
            )
        ]
    )
    return fig


if __name__ == "__main__":
    OUT_DIR_EXPERIMENT = Path("../out_dir/experiment")
    TEST_PATH = Path("../test/test_data/test_db.csv")
    result = ReportFactory(TEST_PATH).inflow_by_category()

    fig_out = pie_chart_inflow(result)
    fig_out.show()
    py.offline.plot(
        fig_out, filename=str(OUT_DIR_EXPERIMENT / "one.html")
    )  # r"C:\Users\18247\Documents\Software\Quartalsbericht_Refactored\out_dir\experiment")
