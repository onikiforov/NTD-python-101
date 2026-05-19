from pydantic import BaseModel, ConfigDict, Field

from tests.models.pydantic.epic_ref_pydantic_model import EpicRef
from tests.models.pydantic.neighbors_pydantic_model import Neighbors
from tests.models.pydantic.project_extra_info_pydantic_model import ProjectExtraInfo
from tests.models.pydantic.status_extra_info_pydantic_model import StatusExtraInfo
from tests.models.pydantic.user_extra_info_pydantic_model import UserExtraInfo


class UserStory(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    backlog_order: int
    blocked_note: str
    blocked_note_html: str
    client_requirement: bool
    comment: str
    created_date: str
    due_date_reason: str
    due_date_status: str
    id: int
    is_blocked: bool
    is_closed: bool
    is_voter: bool
    is_watcher: bool
    kanban_order: int
    modified_date: str
    owner: int
    project: int
    ref: int
    sprint_order: int
    status: int
    subject: str
    team_requirement: bool
    total_attachments: int
    total_comments: int
    total_voters: int
    total_watchers: int
    version: int
    assigned_to: int | None = None
    assigned_to_extra_info: UserExtraInfo | None = None
    assigned_users: list = Field(default_factory=list)
    description: str | None = None
    description_html: str | None = None
    due_date: str | None = None
    epic_order: int | None = None
    epics: list[EpicRef] | None = None
    external_reference: str | None = None
    finish_date: str | None = None
    from_task_ref: int | None = None
    generated_from_issue: int | None = None
    generated_from_task: int | None = None
    milestone: int | None = None
    milestone_name: str | None = None
    milestone_slug: str | None = None
    neighbors: Neighbors | None = None
    origin_issue: int | None = None
    origin_task: int | None = None
    owner_extra_info: UserExtraInfo
    points: dict[str, int | None] = Field(default_factory=dict)
    project_extra_info: ProjectExtraInfo
    status_extra_info: StatusExtraInfo
    swimlane: int | None = None
    tags: list[list] = Field(default_factory=list) # tags is a list of [name, color|null] pairs per Taiga API
    tasks: list = Field(default_factory=list)
    total_points: float | None = None
    tribe_gig: str | None = None
    watchers: list[int] = Field(default_factory=list)
