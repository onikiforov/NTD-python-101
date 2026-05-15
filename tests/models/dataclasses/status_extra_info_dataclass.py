from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StatusExtraInfo:
    name: str
    color: str
    is_closed: bool

    @classmethod
    def from_dict(cls, data: dict) -> "StatusExtraInfo":
        required = ("name", "color", "is_closed")
        for f in required:
            if f not in data:
                raise ValueError(f"Missing required field: {f!r}")
        return cls(name=data["name"], color=data["color"], is_closed=data["is_closed"])
