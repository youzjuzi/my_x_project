from pydantic import BaseModel


class OfferPayload(BaseModel):
    sdp: str
    type: str
    mode: str = "letters"
