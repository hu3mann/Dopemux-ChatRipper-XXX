"""Confirmation guard utilities for Dopemux routing."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Protocol


class ConfirmGuard(Protocol):
    """Interface used to gate sensitive routing actions."""

    def confirm(self, action: str, metadata: Mapping[str, Any] | None = None) -> bool:
        """Return ``True`` if the action is permitted."""


class AlwaysConfirmGuard:
    """Guard that approves every action (useful for defaults and tests)."""

    def confirm(self, action: str, metadata: Mapping[str, Any] | None = None) -> bool:  # noqa: D401
        return True


class CallableConfirmGuard:
    """Wrap a callback inside a :class:`ConfirmGuard` implementation."""

    def __init__(self, callback: Callable[[str, Mapping[str, Any] | None], bool]) -> None:
        self._callback = callback

    def confirm(self, action: str, metadata: Mapping[str, Any] | None = None) -> bool:
        return self._callback(action, metadata)
