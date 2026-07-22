"""Session factory wiring CLI inputs to router implementations."""

from __future__ import annotations

from typing import Any, Mapping

from chatx.dopemux.guards import AlwaysConfirmGuard, ConfirmGuard
from chatx.dopemux.router.mobile import MobileControlRouter, RoutePolicy
from chatx.dopemux.router.base import RouterDecision
from chatx.dopemux.session import ProfileOverlay, Session, SessionMode


class DefaultRouter:
    """Fallback router used by standard sessions."""

    def dispatch(self, action: str, metadata: Mapping[str, Any] | None = None) -> RouterDecision:  # noqa: D401
        return RouterDecision(action=action, metadata=metadata or {}, confirmed=True)


MOBILE_CONTROL_ALLOW_LIST: dict[str, RoutePolicy] = {
    "tap": RoutePolicy(description="Tap on the screen"),
    "swipe": RoutePolicy(description="Swipe gesture"),
    "home": RoutePolicy(description="Return to home screen", requires_confirmation=True),
    "open_app": RoutePolicy(description="Open an application", requires_confirmation=True),
    "close_app": RoutePolicy(description="Close an application"),
    "type_text": RoutePolicy(description="Type text input", requires_confirmation=True),
}


class SessionFactory:
    """Factory responsible for building sessions for the CLI."""

    def __init__(
        self,
        *,
        confirm_guard: ConfirmGuard | None = None,
        allow_list: Mapping[str, RoutePolicy] | None = None,
    ) -> None:
        self._default_guard = confirm_guard or AlwaysConfirmGuard()
        self._mobile_allow_list = dict(allow_list or MOBILE_CONTROL_ALLOW_LIST)

    def create_session(
        self,
        *,
        mode: SessionMode,
        profile_overlay: ProfileOverlay | None = None,
        confirm_guard: ConfirmGuard | None = None,
    ) -> Session:
        """Create a session given the desired mode."""

        if mode is SessionMode.HAPPY:
            router = MobileControlRouter(
                allow_list=self._mobile_allow_list,
                confirm_guard=confirm_guard or self._default_guard,
            )
        else:
            router = DefaultRouter()

        return Session(mode=mode, router=router, profile_overlay=profile_overlay)
