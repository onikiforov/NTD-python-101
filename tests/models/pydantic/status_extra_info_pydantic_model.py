from pydantic import BaseModel, ConfigDict

class StatusExtraInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    color: str
    is_closed: bool
