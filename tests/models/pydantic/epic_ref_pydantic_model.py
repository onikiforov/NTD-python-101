from pydantic import BaseModel, ConfigDict

from tests.models.pydantic.project_extra_info_pydantic_model import ProjectExtraInfo


class EpicRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    ref: int
    subject: str
    color: str
    project: ProjectExtraInfo
