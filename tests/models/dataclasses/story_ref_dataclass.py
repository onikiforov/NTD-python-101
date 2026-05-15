from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoryRef:
    id: int
    ref: int
    subject: str

    @classmethod
    def from_dict(cls, data: dict) -> "StoryRef":
        required = ("id", "ref", "subject")
        for f in required:
            if f not in data:
                raise ValueError(f"Missing required field: {f!r}")
        return cls(id=data["id"], ref=data["ref"], subject=data["subject"])
