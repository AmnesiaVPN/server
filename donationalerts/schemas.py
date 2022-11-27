import datetime

from pydantic import BaseModel


class Donation(BaseModel):
    id: int
    message: str | None
    created_at: datetime.datetime
