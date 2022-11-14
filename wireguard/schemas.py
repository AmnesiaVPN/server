import datetime
import uuid

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
    enabled: bool
    uuid: uuid.UUID
    latest_handshake_at: datetime.datetime | None = Field(alias='latestHandshakeAt')
    name: str
    persistent_keepalive: str = Field(alias='persistentKeepalive')
    public_key: str = Field(alias='publicKey')
    transfer_rx: int = Field(alias='transferRx')
    transfer_tx: int = Field(alias='transferTx')
    updated_at: datetime.datetime = Field(alias='updatedAt')
