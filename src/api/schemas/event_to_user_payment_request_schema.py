from pydantic import BaseModel


class EventToUserPaymentRequestSchema(BaseModel):
    amount: int