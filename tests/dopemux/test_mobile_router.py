from __future__ import annotations

import pytest

from chatx.dopemux.guards import CallableConfirmGuard
from chatx.dopemux.router.mobile import MobileControlRouter, RoutePolicy
from chatx.dopemux.router.base import RoutingError


@pytest.fixture()
def allow_list() -> dict[str, RoutePolicy]:
    return {
        "tap": RoutePolicy(),
        "open_app": RoutePolicy(requires_confirmation=True),
    }


def test_dispatch_allows_listed_action(allow_list: dict[str, RoutePolicy]) -> None:
    router = MobileControlRouter(allow_list, CallableConfirmGuard(lambda *_: True))

    decision = router.dispatch("tap", {"x": 10, "y": 20})

    assert decision.action == "tap"
    assert decision.metadata == {"x": 10, "y": 20}
    assert decision.confirmed is True


def test_dispatch_rejects_unlisted_action(allow_list: dict[str, RoutePolicy]) -> None:
    router = MobileControlRouter(allow_list, CallableConfirmGuard(lambda *_: True))

    with pytest.raises(RoutingError):
        router.dispatch("swipe")


def test_dispatch_respects_confirmation_guard(allow_list: dict[str, RoutePolicy]) -> None:
    router = MobileControlRouter(allow_list, CallableConfirmGuard(lambda *_: False))

    with pytest.raises(RoutingError):
        router.dispatch("open_app")
