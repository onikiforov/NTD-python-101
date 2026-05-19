from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserExtraInfo:
    id: int
    username: str
    full_name_display: str
    gravatar_id: str
    is_active: bool
    photo: str | None
    big_photo: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "UserExtraInfo":
        required = ("id", "username", "full_name_display", "gravatar_id", "is_active")
        for f in required:
            if f not in data:
                raise ValueError(f"Missing required field: {f!r}")
        return cls(
            id=data["id"],
            username=data["username"],
            full_name_display=data["full_name_display"],
            gravatar_id=data["gravatar_id"],
            is_active=data["is_active"],
            photo=data.get("photo"),
            big_photo=data.get("big_photo"),
        )
