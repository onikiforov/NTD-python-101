from pydantic import BaseModel, ConfigDict

from tests.models.pydantic.story_ref_pydantic_model import StoryRef


class Neighbors(BaseModel):
    model_config = ConfigDict(extra="ignore")

    previous: StoryRef | None = None
    next: StoryRef | None = None
