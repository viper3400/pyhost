import sys

from tool_host import cli


def test_cli_passes_default_env_file(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(sys, "argv", ["pyhost"])

    cli.main()

    assert calls[0][1]["env_file"] == ".env"


def test_cli_accepts_custom_env_file(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(sys, "argv", ["pyhost", "--env-file", "host.env"])

    cli.main()

    assert calls[0][1]["env_file"] == "host.env"
