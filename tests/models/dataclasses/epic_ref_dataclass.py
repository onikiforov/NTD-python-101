from dataclasses import dataclass

from tests.models.dataclasses.project_extra_info_dataclass import ProjectExtraInfo


@dataclass(frozen=True, slots=True)
class EpicRef:
    id: int
    ref: int
    subject: str
    color: str
    project: ProjectExtraInfo

    @classmethod
    def from_dict(cls, data: dict) -> "EpicRef":
        required = ("id", "ref", "subject", "color", "project")
        for f in required:
            if f not in data:
                raise ValueError(f"Missing required field: {f!r}")
        return cls(
            id=data["id"],
            ref=data["ref"],
            subject=data["subject"],
            color=data["color"],
            project=ProjectExtraInfo.from_dict(data["project"]),
        )
