from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, ValidationError, field_validator

from ..extractors.dom_utils import clean_text, normalize_fb_url

FriendshipStatus = Literal["CAN_REQUEST", "FRIEND", "FOLLOWING", "REQUEST_SENT", "UNKNOWN"]

class Follower(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique numeric ID, if available.")
    image: Optional[str] = Field(default=None, description="Profile picture URL (public variant).")
    title: Optional[str] = Field(default=None, description="Mirror of display name (platform 'title').")
    subtitle_text: Optional[str] = Field(default=None, description="Public location or tagline next to name.")
    url: Optional[str] = Field(default=None, description="Canonical profile URL.")
    friendship_status: FriendshipStatus = Field(default="UNKNOWN")
    gender: Optional[Literal["MALE", "FEMALE", "OTHER"]] = None
    name: str = Field(description="Full display name.")
    short_name: Optional[str] = Field(default=None, description="First name or nickname.")

    @field_validator("url")
    @classmethod
    def _normalize_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = normalize_fb_url(v)
        return v or None

    @field_validator("gender", mode="before")
    @classmethod
    def _norm_gender(cls, v):
        if v is None:
            return None
        s = str(v).strip().upper()
        if s in {"MALE", "FEMALE", "OTHER"}:
            return s
        # Unknown/unsupported labels are mapped to None
        return None

    @field_validator("friendship_status", mode="before")
    @classmethod
    def _norm_friendship(cls, v):
        if v is None:
            return "UNKNOWN"
        s = str(v).strip().upper()
        allowed = {"CAN_REQUEST", "FRIEND", "FOLLOWING", "REQUEST_SENT", "UNKNOWN"}
        return s if s in allowed else "UNKNOWN"

    @field_validator("name", mode="before")
    @classmethod
    def _require_name(cls, v):
        s = clean_text(v)
        if not s:
            raise ValueError("name is required")
        return s

    @field_validator("short_name", mode="before")
    @classmethod
    def _derive_short_name(cls, v, info):
        if v:
            return clean_text(v)
        # Derive from 'name' if not provided
        data = info.data
        name = clean_text(data.get("name")) if data else None
        if name:
            return name.split(" ")[0]
        return None

    @field_validator("title", mode="before")
    @classmethod
    def _default_title(cls, v, info):
        if v:
            return clean_text(v)
        data = info.data
        name = clean_text(data.get("name")) if data else None
        return name or None

def normalize_record_list(raw_records: List[dict]) -> List[Follower]:
    normalized: List[Follower] = []
    for idx, rec in enumerate(raw_records):
        try:
            model = Follower.model_validate(rec)
        except ValidationError as e:
            # Skip invalid record but continue processing
            # In a production system, collect and report these.
            continue
        normalized.append(model)
    return normalized