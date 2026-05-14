from pydantic import BaseModel, ConfigDict, Field


class UserStory(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int
    ref: int
    subject: str
    project: int
    status: int
    version: int
    created_date: str
    modified_date: str
    description: str | None = None
    assigned_to: int | None = None
    tags: list[str] = Field(default_factory=list)
