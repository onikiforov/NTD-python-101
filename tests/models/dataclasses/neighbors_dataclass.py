from dataclasses import dataclass

from tests.models.dataclasses.story_ref_dataclass import StoryRef


@dataclass(frozen=True, slots=True)
class Neighbors:
    previous: StoryRef | None
    next: StoryRef | None

    @classmethod
    def from_dict(cls, data: dict) -> "Neighbors":
        return cls(
            previous=StoryRef.from_dict(data["previous"]) if data.get("previous") else None,
            next=StoryRef.from_dict(data["next"]) if data.get("next") else None,
        )
