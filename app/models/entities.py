from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    role: str = Field(default="analista")


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    owner_id: int = Field(foreign_key="user.id")
    policy: str = "Solo fuentes públicas/autorizadas"


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    url: str
    allowed_domains: str = ""
    excluded_domains: str = ""
    crawl_depth: int = 1
    selector_rule: str = "body"


class CrawlRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    source_id: int = Field(foreign_key="source.id")
    status: str = "pending"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    error: Optional[str] = None


class RawDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="crawlrun.id")
    url: str
    html: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class ProcessedDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="crawlrun.id")
    url: str
    text: str
    language: str = "unknown"
    sentiment_label: str = "neutral"
    sentiment_score: float = 0.0
    confidence: float = 0.0
    topic: str = "general"
    created_at: datetime = Field(default_factory=datetime.utcnow)
