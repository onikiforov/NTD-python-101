from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProjectExtraInfo:
    id: int
    name: str
    slug: str
    logo_small_url: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectExtraInfo":
        required = ("id", "name", "slug")
        for f in required:
            if f not in data:
                raise ValueError(f"Missing required field: {f!r}")
        return cls(
            id=data["id"],
            name=data["name"],
            slug=data["slug"],
            logo_small_url=data.get("logo_small_url"),
        )
