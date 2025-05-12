from pydantic import BaseModel


class BalanceSchema(BaseModel):
    balance: int