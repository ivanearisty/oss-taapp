from pydantic import BaseModel, Field

class MessageSchema(BaseModel):
    """The JSON representation of an email message."""
    id: str
    from_address: str = Field(..., alias="from_")
    to_address: str = Field(..., alias="to")
    date: str
    subject: str
    body: str

    class Config:
        # Allows using the `from_` field name in the Pydantic model
        populate_by_name = True

class StatusResponse(BaseModel):
    """A generic status response for operations like delete or mark-as-read."""
    status: str
    message: str