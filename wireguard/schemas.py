import datetime
from uuid import UUID

from pydantic import BaseModel, Field

__all__ = ('User', 'UserCreated')


class UserCreated(BaseModel):
    address: str
    created_at: datetime.datetime = Field(alias='createdAt')
    enabled: bool
    name: str
    pre_shared_key: str = Field(alias='preSharedKey')
    public_key: str = Field(alias='publicKey')
    updated_at: datetime.datetime = Field(alias='updatedAt')


class User(BaseModel):
    address: str
    created_at: datetime.datetime = Field(alias='createdAt')
    is_enabled: bool = Field(alias='enabled')
    uuid: UUID = Field(alias='id')
    latest_handshake_at: datetime.datetime | None = Field(alias='latestHandshakeAt')
    name: str
    updated_at: datetime.datetime = Field(alias='updatedAt')
