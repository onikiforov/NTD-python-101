from pydantic import BaseModel, ConfigDict, Field


class OwnerExtraInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    username: str
    full_name_display: str
    gravatar_id: str
    is_active: bool
    photo: str | None = None
    big_photo: str | None = None


class ProjectExtraInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    slug: str
    logo_small_url: str | None = None


class StatusExtraInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    color: str
    is_closed: bool


class UserStory(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int
    ref: int
    subject: str
    project: int
    status: int
    version: int
    created_date: str
    modified_date: str
    owner: int
    backlog_order: int
    sprint_order: int
    kanban_order: int
    is_blocked: bool
    is_closed: bool
    is_voter: bool
    is_watcher: bool
    client_requirement: bool
    team_requirement: bool
    total_comments: int
    total_watchers: int
    total_voters: int
    total_attachments: int
    blocked_note: str
    comment: str
    due_date_reason: str
    due_date_status: str
    # tags is a list of [name, color|null] pairs per Taiga API
    tags: list[list] = Field(default_factory=list)
    watchers: list[int] = Field(default_factory=list)
    tasks: list = Field(default_factory=list)
    assigned_users: list = Field(default_factory=list)
    points: dict[str, int | None] = Field(default_factory=dict)
    owner_extra_info: OwnerExtraInfo
    project_extra_info: ProjectExtraInfo
    status_extra_info: StatusExtraInfo
    assigned_to: int | None = None
    assigned_to_extra_info: dict | None = None
    description: str | None = None
    due_date: str | None = None
    epic_order: int | None = None
    epics: list | None = None
    external_reference: str | None = None
    finish_date: str | None = None
    generated_from_issue: int | None = None
    generated_from_task: int | None = None
    milestone: int | None = None
    milestone_name: str | None = None
    milestone_slug: str | None = None
    origin_issue: int | None = None
    origin_task: int | None = None
    total_points: float | None = None
    tribe_gig: str | None = None
