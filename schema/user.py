from pydantic import BaseModel

class Subscriber(BaseModel):
    endpoint: str
    keys: dict
    userId: str