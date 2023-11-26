from dataclasses import dataclass, field
from datetime import datetime

import pandera as pa


@dataclass
class ProfitNLoss:
    expense_fix: float
    expense_var: float
    total_expense: float = field(init=False)
    income_fix: float
    income_var: float
    total_income: float = field(init=False)
    profit_n_loss: float = field(init=False)

    def __post_init__(self):
        self.total_expense = self.expense_fix + self.expense_var
        self.total_income = self.income_fix + self.income_var
        self.profit_n_loss = self.total_expense + self.total_income


class QuarterlyInputData(pa.DataFrameModel):
    Buchungstag: datetime = pa.Field()
    Wertstellung: object = pa.Field(nullable=True)
    Betrag: float = pa.Field()
    Verwendungszweck: str = pa.Field()
    prep_Month: str = pa.Field(
        isin=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
    )
    prep_Year: int = pa.Field()
    prep_Type: str = pa.Field(isin=["Einnahme", "Ausgabe", "Umbuchung"])
    prep_Recurring: bool = pa.Field()
    prep_Category: str = pa.Field()
