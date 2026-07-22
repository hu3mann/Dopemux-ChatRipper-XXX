"""Routing primitives for Dopemux sessions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class RoutingError(RuntimeError):
    """Raised when a routing request cannot be satisfied."""


@dataclass(frozen=True)
class RouterDecision:
    """Represents the outcome of dispatching a routing request."""

    action: str
    metadata: Mapping[str, Any]
    confirmed: bool


class BaseRouter(Protocol):
    """Interface implemented by Dopemux routers."""

    def dispatch(self, action: str, metadata: Mapping[str, Any] | None = None) -> RouterDecision:
        """Dispatch an action and return the resulting decision."""
