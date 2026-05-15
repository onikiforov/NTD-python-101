from pydantic import BaseModel, ConfigDict

class StoryRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    ref: int
    subject: str
