import datetime

from pydantic import BaseModel


class Donation(BaseModel):
    id: int
    message: str
    amount: int
    currency: str
    created_at: datetime.datetime
