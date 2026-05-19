from pydantic import BaseModel, ConfigDict

class UserExtraInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    username: str
    full_name_display: str
    gravatar_id: str
    is_active: bool
    photo: str | None = None
    big_photo: str | None = None
