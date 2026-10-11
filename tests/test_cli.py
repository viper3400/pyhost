import sys

from tool_host import cli


def test_cli_passes_default_env_file(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(sys, "argv", ["pyhost"])

    cli.main()

    assert calls[0][1]["env_file"] == ".env"
    assert calls[0][1]["forwarded_allow_ips"] == "127.0.0.1"


def test_cli_accepts_custom_env_file(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(sys, "argv", ["pyhost", "--env-file", "host.env"])

    cli.main()

    assert calls[0][1]["env_file"] == "host.env"


def test_cli_accepts_forwarded_proxy_ips(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(sys, "argv", ["pyhost", "--forwarded-allow-ips", "172.20.0.5"])

    cli.main()

    assert calls[0][1]["forwarded_allow_ips"] == "172.20.0.5"


def test_cli_reads_forwarded_proxy_ips_from_environment(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(sys, "argv", ["pyhost"])
    monkeypatch.setenv("PYHOST_FORWARDED_ALLOW_IPS", "172.20.0.0/16")

    cli.main()

    assert calls[0][1]["forwarded_allow_ips"] == "172.20.0.0/16"
