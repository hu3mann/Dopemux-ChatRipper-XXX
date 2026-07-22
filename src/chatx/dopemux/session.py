"""Session primitives for the Dopemux orchestration layer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping
import json

from chatx.dopemux.router.base import BaseRouter


class SessionMode(str, Enum):
    """Supported session modes."""

    STANDARD = "standard"
    HAPPY = "happy"  # Mobile-control session alias


@dataclass(frozen=True)
class ProfileOverlay:
    """Represents an optional overlay applied to a session profile."""

    name: str
    data: Mapping[str, Any]

    @classmethod
    def from_path(cls, path: Path) -> "ProfileOverlay":
        """Load a profile overlay from a JSON document."""

        if not path.exists():
            msg = f"Overlay profile not found: {path}"
            raise FileNotFoundError(msg)

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:  # pragma: no cover - propagated
            raise RuntimeError(f"Unable to read overlay file: {path}") from exc

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Overlay must be valid JSON: {path}") from exc

        if not isinstance(payload, dict):
            raise ValueError("Overlay JSON must describe an object")

        name = str(payload.get("name")) if payload.get("name") else path.stem
        return cls(name=name, data=payload)


@dataclass(slots=True)
class Session:
    """Container describing an active Dopemux session."""

    mode: SessionMode
    router: BaseRouter
    profile_overlay: ProfileOverlay | None = None
