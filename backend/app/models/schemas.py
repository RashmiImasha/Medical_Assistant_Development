from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class DocumentUploadResponse(BaseModel):

    id:str
    filename:str
    message: str

class FinancialMetrics(BaseModel):

    revenue: str | int | None = Field(None, alias="Revenue")
    net_income: str | int | None = Field(None, alias="Net Income")
    operating_income: str | int | None = Field(None, alias="Operating Income")
    cash_flow: str | int | None = Field(None, alias="Cash Flow from Operating Activities")
    total_assets: str | int | None = Field(None, alias="Total Assets")
    total_liabilities: str | int | None = Field(None, alias="Total Liabilities")
    risk_factors: str | list | None = Field(None, alias="Top Risk Factors")
    growth_drivers: str | list | None = Field(None, alias="Top Growth Drivers")


class ExtractMetricsResponse(BaseModel):

    id: str
    filename: str
    metrics: FinancialMetrics




