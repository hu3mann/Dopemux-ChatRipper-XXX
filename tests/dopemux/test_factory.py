from __future__ import annotations

from chatx.dopemux.factory import SessionFactory
from chatx.dopemux.router.mobile import MobileControlRouter
from chatx.dopemux.session import ProfileOverlay, SessionMode


def test_factory_creates_happy_session(tmp_path) -> None:
    overlay_path = tmp_path / "overlay.json"
    overlay_path.write_text("{""name"": ""mobile""}", encoding="utf-8")

    overlay = ProfileOverlay.from_path(overlay_path)
    factory = SessionFactory()

    session = factory.create_session(mode=SessionMode.HAPPY, profile_overlay=overlay)

    assert session.mode is SessionMode.HAPPY
    assert isinstance(session.router, MobileControlRouter)
    assert session.profile_overlay is overlay


def test_factory_creates_standard_session() -> None:
    factory = SessionFactory()

    session = factory.create_session(mode=SessionMode.STANDARD)

    assert session.mode is SessionMode.STANDARD
    assert not isinstance(session.router, MobileControlRouter)
