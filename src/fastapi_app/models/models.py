"""
Modules to specify Pydantic models for endpoints
"""

from pydantic import BaseModel


class ModelMetrics(BaseModel):

    positive_precision: float
    positive_recall: float
    positive_f1: float
    macro_precision: float
    macro_recall: float
    macro_f1: float


class ModelInfo(BaseModel):

    model_name: str
    model_version: int
    model_metrics: ModelMetrics


class Transaction(BaseModel):

    id: str
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float
    Class: int


class TransactionPrediction(Transaction):

    is_fraud: int
