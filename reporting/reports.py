from datetime import datetime
from pathlib import Path

import pandas as pd
from models import ProfitNLoss


class ReportFactory:
    master_raw_data: pd.DataFrame

    def __init__(self, path: Path):
        self.master_raw_data = self.read_data(path)

    def read_data(self, path: Path) -> pd.DataFrame:
        data = pd.read_csv(
            path,
            delimiter=";",
            decimal=".",
            parse_dates=["Buchungstag"],
            date_parser=lambda x: datetime.strptime(x, "%d.%m.%Y"),
        )
        return data

    def show_biggest_expenses(self, n: int = 5):
        """List the n biggest expenses"""
        return self.master_raw_data.nsmallest(n=n, columns=["Betrag"])[
            ["Betrag", "Buchungstag", "prep_Month", "prep_Category", "Verwendungszweck"]
        ]

    def profit_n_loss(self):
        calc_profit_n_loss = (
            self.master_raw_data.drop("Buchungstag", axis=1)
            .groupby(["prep_Type", "prep_Recurring"])
            .sum()
            .round(decimals=2)
        )

        return ProfitNLoss(
            expense_fix=calc_profit_n_loss.loc[("Ausgabe", True), "Betrag"],
            expense_var=calc_profit_n_loss.loc[("Ausgabe", False), "Betrag"],
            income_fix=calc_profit_n_loss.loc[("Einnahme", True), "Betrag"],
            income_var=calc_profit_n_loss.loc[("Einnahme", False), "Betrag"],
        )

    def income_vs_expense(self):
        calc_income_vs_expense = (
            self.master_raw_data.drop("Buchungstag", axis=1)
            .groupby(["prep_Month", "prep_Type"])
            .sum()["Betrag"]
        )
        return calc_income_vs_expense

    def cumulated_overflow_by_month(self):
        only_income_outflow = self.master_raw_data.drop("Buchungstag", axis=1).copy()
        only_income_outflow = only_income_outflow[
            only_income_outflow["prep_Type"] != "Umbuchung"
        ]
        cumulated_overflow_by_month = only_income_outflow.groupby(["prep_Month"]).sum()[
            "Betrag"
        ]
        return cumulated_overflow_by_month

    def outflow_fix_vs_var(self):
        only_outflow = self.master_raw_data.drop("Buchungstag", axis=1).copy()
        only_outflow = only_outflow[only_outflow["prep_Type"] == "Ausgabe"]
        outflow_fix_vs_var = only_outflow.groupby(
            ["prep_Month", "prep_Recurring"]
        ).sum()["Betrag"]
        return outflow_fix_vs_var

    def inflow_fix_vs_var(self):
        only_inflow = self.master_raw_data.drop("Buchungstag", axis=1).copy()
        only_inflow = only_inflow[only_inflow["prep_Type"] == "Einnahme"]
        inflow_fix_vs_var = only_inflow.groupby(["prep_Month", "prep_Recurring"]).sum()[
            "Betrag"
        ]
        return inflow_fix_vs_var

    def outflow_by_category(self):
        only_outflow = self.master_raw_data.drop("Buchungstag", axis=1).copy()
        only_outflow = only_outflow[only_outflow["prep_Type"] == "Ausgabe"]
        outflow_category = only_outflow.groupby(["prep_Category"]).sum()["Betrag"]

        return outflow_category * (-1)

    def inflow_by_category(self):
        only_inflow = self.master_raw_data.drop("Buchungstag", axis=1).copy()
        only_inflow = only_inflow[only_inflow["prep_Type"] == "Einnahme"]
        inflow_category = only_inflow.groupby(["prep_Category"]).sum()["Betrag"]
        return inflow_category

    def budget(self):
        data = self.outflow_by_category().copy()
        BUDGET_DICT = {"Wohnen": 450, "Studium": 100}
        res = {
            key: val for key, val in sorted(BUDGET_DICT.items(), key=lambda ele: ele[0])
        }  # sort dict
        data = data[list(BUDGET_DICT.keys())]
        data.sort_index(inplace=True)
        data = data.reset_index()
        data["Betrag"] = data["Betrag"].abs()

        data["Budget"] = res.values()
        data["Usage"] = round(data["Betrag"] / data["Budget"], 4)

        return data
