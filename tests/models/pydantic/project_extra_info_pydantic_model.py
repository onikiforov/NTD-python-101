from pydantic import BaseModel, ConfigDict

class ProjectExtraInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    slug: str
    logo_small_url: str | None = None
