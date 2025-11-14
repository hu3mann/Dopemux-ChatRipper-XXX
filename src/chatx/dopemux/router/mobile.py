"""Mobile control router implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from chatx.dopemux.guards import ConfirmGuard
from chatx.dopemux.router.base import RouterDecision, RoutingError


@dataclass(frozen=True)
class RoutePolicy:
    """Policy associated with a routed mobile action."""

    requires_confirmation: bool = False
    description: str | None = None


class MobileControlRouter:
    """Router dedicated to mobile-control "happy" sessions."""

    def __init__(
        self,
        allow_list: Mapping[str, RoutePolicy],
        confirm_guard: ConfirmGuard,
    ) -> None:
        self._allow_list = dict(allow_list)
        self._confirm_guard = confirm_guard

    def dispatch(self, action: str, metadata: Mapping[str, Any] | None = None) -> RouterDecision:
        """Dispatch a mobile control action after applying policy checks."""

        if action not in self._allow_list:
            raise RoutingError(f"Action '{action}' is not permitted in mobile-control mode")

        policy = self._allow_list[action]
        confirmed = True
        if policy.requires_confirmation:
            confirmed = self._confirm_guard.confirm(action, metadata)
            if not confirmed:
                raise RoutingError(f"Action '{action}' was rejected by confirmation guard")

        return RouterDecision(action=action, metadata=metadata or {}, confirmed=confirmed)

    @property
    def allow_list(self) -> Mapping[str, RoutePolicy]:
        """Expose the allow-list for inspection/testing purposes."""

        return dict(self._allow_list)
