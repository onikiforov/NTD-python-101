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
    blocked_note_html: str
    comment: str
    due_date_reason: str
    due_date_status: str
    tags: tuple
    watchers: tuple
    tasks: tuple
    assigned_users: tuple
    points: dict
    owner_extra_info: UserExtraInfo
    project_extra_info: ProjectExtraInfo
    status_extra_info: StatusExtraInfo
    assigned_to: int | None = None
    assigned_to_extra_info: UserExtraInfo | None = None
    description: str | None = None
    description_html: str | None = None
    due_date: str | None = None
    epic_order: int | None = None
    epics: tuple | None = None
    external_reference: str | None = None
    finish_date: str | None = None
    generated_from_issue: int | None = None
    generated_from_task: int | None = None
    milestone: int | None = None
    milestone_name: str | None = None
    milestone_slug: str | None = None
    neighbors: Neighbors | None = None
    origin_issue: int | None = None
    origin_task: int | None = None
    total_points: float | None = None
    tribe_gig: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "UserStory":
        required = (
            "id", "ref", "subject", "project", "status", "version",
            "created_date", "modified_date", "owner", "backlog_order",
            "sprint_order", "kanban_order", "is_blocked", "is_closed",
            "is_voter", "is_watcher", "client_requirement", "team_requirement",
            "total_comments", "total_watchers", "total_voters", "total_attachments",
            "blocked_note", "blocked_note_html", "comment", "due_date_reason",
            "due_date_status", "tags", "watchers", "tasks", "assigned_users",
            "points", "owner_extra_info", "project_extra_info", "status_extra_info",
        )
        for f in required:
            if f not in data:
                raise ValueError(f"Missing required field: {f!r}")
        return cls(
            id=data["id"],
            ref=data["ref"],
            subject=data["subject"],
            project=data["project"],
            status=data["status"],
            version=data["version"],
            created_date=data["created_date"],
            modified_date=data["modified_date"],
            owner=data["owner"],
            backlog_order=data["backlog_order"],
            sprint_order=data["sprint_order"],
            kanban_order=data["kanban_order"],
            is_blocked=data["is_blocked"],
            is_closed=data["is_closed"],
            is_voter=data["is_voter"],
            is_watcher=data["is_watcher"],
            client_requirement=data["client_requirement"],
            team_requirement=data["team_requirement"],
            total_comments=data["total_comments"],
            total_watchers=data["total_watchers"],
            total_voters=data["total_voters"],
            total_attachments=data["total_attachments"],
            blocked_note=data["blocked_note"],
            blocked_note_html=data["blocked_note_html"],
            comment=data["comment"],
            due_date_reason=data["due_date_reason"],
            due_date_status=data["due_date_status"],
            tags=tuple(tuple(t) for t in data["tags"]),
            watchers=tuple(data["watchers"]),
            tasks=tuple(data["tasks"]),
            assigned_users=tuple(data["assigned_users"]),
            points=dict(data["points"]),
            owner_extra_info=UserExtraInfo.from_dict(data["owner_extra_info"]),
            project_extra_info=ProjectExtraInfo.from_dict(data["project_extra_info"]),
            status_extra_info=StatusExtraInfo.from_dict(data["status_extra_info"]),
            assigned_to=data.get("assigned_to"),
            assigned_to_extra_info=UserExtraInfo.from_dict(data["assigned_to_extra_info"]) if data.get("assigned_to_extra_info") else None,
            description=data.get("description"),
            description_html=data.get("description_html"),
            due_date=data.get("due_date"),
            epic_order=data.get("epic_order"),
            epics=tuple(EpicRef.from_dict(e) for e in data["epics"]) if data.get("epics") is not None else None,
            external_reference=data.get("external_reference"),
            finish_date=data.get("finish_date"),
            generated_from_issue=data.get("generated_from_issue"),
            generated_from_task=data.get("generated_from_task"),
            milestone=data.get("milestone"),
            milestone_name=data.get("milestone_name"),
            milestone_slug=data.get("milestone_slug"),
            neighbors=Neighbors.from_dict(data["neighbors"]) if data.get("neighbors") else None,
            origin_issue=data.get("origin_issue"),
            origin_task=data.get("origin_task"),
            total_points=data.get("total_points"),
            tribe_gig=data.get("tribe_gig"),
        )
