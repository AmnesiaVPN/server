import datetime

from pydantic import BaseModel


class DonationalertsPayment(BaseModel):
    id: int
    message: str | None
    created_at: datetime.datetime
