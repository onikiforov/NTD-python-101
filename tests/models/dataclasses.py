from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserStory:
    id: int
    ref: int
    subject: str
    project: int
    status: int
    version: int
    created_date: str
    modified_date: str

    @classmethod
    def from_dict(cls, data: dict) -> "UserStory":
        required = ("id", "ref", "subject", "project", "status", "version", "created_date", "modified_date")
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field!r}")
        return cls(
            id=data["id"],
            ref=data["ref"],
            subject=data["subject"],
            project=data["project"],
            status=data["status"],
            version=data["version"],
            created_date=data["created_date"],
            modified_date=data["modified_date"],
        )
