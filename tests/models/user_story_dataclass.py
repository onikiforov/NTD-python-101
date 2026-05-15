from dataclasses import dataclass

from tests.models.epic_ref_dataclass import EpicRef
from tests.models.neighbors_dataclass import Neighbors
from tests.models.project_extra_info_dataclass import ProjectExtraInfo
from tests.models.status_extra_info_dataclass import StatusExtraInfo
from tests.models.user_extra_info_dataclass import UserExtraInfo


@dataclass(frozen=True, slots=True)
class UserStory:
    attachments: list
    assigned_users: tuple
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
    owner_extra_info: UserExtraInfo
    points: dict
    project: int
    project_extra_info: ProjectExtraInfo
    ref: int
    sprint_order: int
    status: int
    status_extra_info: StatusExtraInfo
    subject: str
    tags: tuple
    tasks: tuple
    team_requirement: bool
    total_attachments: int
    total_comments: int
    total_voters: int
    total_watchers: int
    version: int
    watchers: tuple
    assigned_to: int | None = None
    assigned_to_extra_info: UserExtraInfo | None = None
    description: str | None = None
    description_html: str | None = None
    due_date: str | None = None
    epic_order: int | None = None
    epics: tuple | None = None
    external_reference: str | None = None
    finish_date: str | None = None
    from_task_ref: int | None = None
    swimlane: int | None = None
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
            assigned_to=data.get("assigned_to"),
            assigned_to_extra_info=UserExtraInfo.from_dict(data["assigned_to_extra_info"]) if data.get(
                "assigned_to_extra_info") else None,
            assigned_users=tuple(data["assigned_users"]),
            attachments=data["attachments"],
            backlog_order=data["backlog_order"],
            blocked_note=data["blocked_note"],
            blocked_note_html=data["blocked_note_html"],
            client_requirement=data["client_requirement"],
            comment=data["comment"],
            created_date=data["created_date"],
            description=data.get("description"),
            description_html=data.get("description_html"),
            due_date=data.get("due_date"),
            due_date_reason=data["due_date_reason"],
            due_date_status=data["due_date_status"],
            epic_order=data.get("epic_order"),
            epics=tuple(EpicRef.from_dict(e) for e in data["epics"]) if data.get("epics") else None,
            external_reference=data.get("external_reference"),
            finish_date=data.get("finish_date"),
            from_task_ref=data.get("from_task_ref"),
            swimlane=data.get("swimlane"),
            generated_from_issue=data.get("generated_from_issue"),
            generated_from_task=data.get("generated_from_task"),
            id=data["id"],
            is_blocked=data["is_blocked"],
            is_closed=data["is_closed"],
            is_voter=data["is_voter"],
            is_watcher=data["is_watcher"],
            kanban_order=data["kanban_order"],
            milestone=data.get("milestone"),
            milestone_name=data.get("milestone_name"),
            milestone_slug=data.get("milestone_slug"),
            modified_date=data["modified_date"],
            neighbors=Neighbors.from_dict(data["neighbors"]) if data.get("neighbors") else None,
            origin_issue=data.get("origin_issue"),
            origin_task=data.get("origin_task"),
            owner=data["owner"],
            owner_extra_info=UserExtraInfo.from_dict(data["owner_extra_info"]),
            points=dict(data["points"]),
            project=data["project"],
            project_extra_info=ProjectExtraInfo.from_dict(data["project_extra_info"]),
            ref=data["ref"],
            sprint_order=data["sprint_order"],
            status=data["status"],
            status_extra_info=StatusExtraInfo.from_dict(data["status_extra_info"]),
            subject=data["subject"],
            tags=tuple(tuple(t) for t in data["tags"]),
            tasks=tuple(data["tasks"]),
            team_requirement=data["team_requirement"],
            total_attachments=data["total_attachments"],
            total_comments=data["total_comments"],
            total_points=data.get("total_points"),
            total_voters=data["total_voters"],
            total_watchers=data["total_watchers"],
            tribe_gig=data.get("tribe_gig"),
            version=data["version"],
            watchers=tuple(data["watchers"]),
        )
