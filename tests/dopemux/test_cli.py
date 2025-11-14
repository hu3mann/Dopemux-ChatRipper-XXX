from __future__ import annotations

from typer.testing import CliRunner

from chatx.dopemux.cli import app


runner = CliRunner()


def test_start_standard_session() -> None:
    result = runner.invoke(app, ["start"])

    assert result.exit_code == 0
    assert "Started standard session" in result.stdout


def test_start_mobile_via_alt_routing() -> None:
    result = runner.invoke(app, ["start", "--alt-routing"])

    assert result.exit_code == 0
    assert "mobile-control" in result.stdout
    assert "legacy" in result.stdout.lower()


def test_start_mobile_via_mobile_alias() -> None:
    result = runner.invoke(app, ["start", "--mobile"])

    assert result.exit_code == 0
    assert "mobile-control" in result.stdout


def test_start_with_profile_overlay(tmp_path) -> None:
    overlay = tmp_path / "overlay.json"
    overlay.write_text("{""name"": ""custom""}", encoding="utf-8")

    result = runner.invoke(app, ["start", "--mobile", "--profile-overlay", str(overlay)])

    assert result.exit_code == 0
    assert "Profile overlay: custom" in result.stdout
