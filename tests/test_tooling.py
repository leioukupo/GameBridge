import hashlib
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from gamebridge.tooling import (
    DWPROTON_RELEASE,
    GE_PROTON_RELEASE,
    LEGENDARY_RELEASES,
    UMU_RELEASE,
    ToolInstaller,
    ToolRelease,
)


class Response(BytesIO):
    headers = {"Content-Length": "11"}

    def geturl(self):
        return "https://release-assets.githubusercontent.com/asset"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_installer_verifies_and_atomically_installs(tmp_path, monkeypatch):
    content = b"hello world"
    release = ToolRelease(
        "test", "https://github.com/legendary-gl/legendary/releases/download/test/tool",
        hashlib.sha256(content).hexdigest(),
    )
    installer = ToolInstaller()
    monkeypatch.setattr(installer, "legendary_release", lambda: release)
    monkeypatch.setattr("urllib.request.urlopen", lambda *_args, **_kwargs: Response(content))
    target = tmp_path / "tools" / "legendary"
    result = installer.install_legendary(target)
    assert target.read_bytes() == content
    assert target.stat().st_mode & 0o111
    assert result["version"] == "test"


class RouteResponse(BytesIO):
    """One served download route, keyed by the URL the installer requested."""

    def __init__(self, content: bytes, url: str) -> None:
        super().__init__(content)
        self.url = url
        self.headers = {"Content-Length": str(len(content))}

    def geturl(self) -> str:
        return self.url

    def __enter__(self) -> "RouteResponse":
        return self

    def __exit__(self, *args) -> None:
        self.close()


GATEWAY_URL = "https://1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com/download/legendary"
OFFICIAL_URL = "https://github.com/example/official"


def routed_release(content: bytes) -> ToolRelease:
    return ToolRelease(
        "test", OFFICIAL_URL, hashlib.sha256(content).hexdigest(), "legendary", GATEWAY_URL
    )


def test_legendary_release_follows_the_child_architecture(monkeypatch, tmp_path):
    """An emulated x86_64 host still runs downloaded CLI tools natively."""
    fake_uname = tmp_path / "uname"
    fake_uname.write_text("#!/bin/sh\nprintf 'aarch64\\n'\n", encoding="utf-8")
    fake_uname.chmod(0o755)
    monkeypatch.setattr("gamebridge.tooling.shutil.which", lambda name: str(fake_uname))
    monkeypatch.setattr("gamebridge.tooling.platform.machine", lambda: "x86_64")

    assert ToolInstaller.child_architecture() == "aarch64"
    assert ToolInstaller().legendary_release() is LEGENDARY_RELEASES["aarch64"]
    assert LEGENDARY_RELEASES["aarch64"].gateway_url is None


def test_legendary_release_falls_back_to_the_host_architecture(monkeypatch):
    monkeypatch.setattr("gamebridge.tooling.shutil.which", lambda _name: None)
    monkeypatch.setattr("gamebridge.tooling.platform.machine", lambda: "AMD64")

    assert ToolInstaller.child_architecture() == "x86_64"
    assert ToolInstaller().legendary_release() is LEGENDARY_RELEASES["x86_64"]


def test_download_falls_back_to_the_official_route_when_the_gateway_is_down(
    tmp_path, monkeypatch
):
    content = b"hello world"
    installer = ToolInstaller()
    attempted: list[str] = []

    def fake_urlopen(request, *_args, **_kwargs):
        attempted.append(request.full_url)
        if "tencentscf.com" in request.full_url:
            raise HTTPError(request.full_url, 502, "Bad Gateway", {}, None)
        return RouteResponse(content, "https://release-assets.githubusercontent.com/asset")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = installer._download(routed_release(content), tmp_path, ".fallback-")

    assert result.read_bytes() == content
    assert attempted == [GATEWAY_URL, OFFICIAL_URL]
    status = installer.progress_status()
    assert status["phase"] == "verifying"
    assert status["source"] == "official"


def test_download_rejects_a_gateway_payload_that_fails_the_pinned_digest(
    tmp_path, monkeypatch
):
    content = b"hello world"
    installer = ToolInstaller()
    attempted: list[str] = []

    def fake_urlopen(request, *_args, **_kwargs):
        attempted.append(request.full_url)
        if "tencentscf.com" in request.full_url:
            return RouteResponse(b"wrong payload", request.full_url)
        return RouteResponse(content, OFFICIAL_URL)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = installer._download(routed_release(content), tmp_path, ".digest-")

    assert result.read_bytes() == content
    assert attempted == [GATEWAY_URL, OFFICIAL_URL]


def test_download_reports_failure_once_every_route_is_down(tmp_path, monkeypatch):
    content = b"hello world"
    installer = ToolInstaller()
    attempted: list[str] = []

    def fake_urlopen(request, *_args, **_kwargs):
        attempted.append(request.full_url)
        raise URLError("Download route temporarily unavailable")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(URLError, match="temporarily unavailable"):
        installer._download(routed_release(content), tmp_path, ".offline-")

    assert attempted == [GATEWAY_URL, OFFICIAL_URL]
    status = installer.progress_status()
    assert status["active"] is False
    assert status["phase"] == "failed"
    assert list(tmp_path.iterdir()) == []


def test_installer_rejects_untrusted_url(tmp_path, monkeypatch):
    installer = ToolInstaller()
    release = ToolRelease("test", "https://example.com/tool", "0" * 64)
    monkeypatch.setattr(installer, "legendary_release", lambda: release)
    with pytest.raises(ValueError, match="allowlisted"):
        installer.install_legendary(tmp_path / "legendary")


def test_ssl_context_requires_a_real_ca_bundle(monkeypatch):
    monkeypatch.setattr("gamebridge.tooling.SYSTEM_CA_FILES", ("/definitely/missing",))
    with pytest.raises(RuntimeError, match="CA certificate"):
        ToolInstaller._ssl_context()


def test_x86_managed_components_use_the_single_region_gateway():
    releases = (
        UMU_RELEASE,
        GE_PROTON_RELEASE,
        DWPROTON_RELEASE,
        LEGENDARY_RELEASES["x86_64"],
    )
    assert all(
        release.gateway_url
        and release.gateway_url.startswith(
            "https://1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com/download/"
        )
        for release in releases
    )
    assert LEGENDARY_RELEASES["aarch64"].gateway_url is None


def test_download_source_is_derived_after_the_gateway_redirect():
    assert ToolInstaller._download_source("https://d.pcs.baidu.com/file/example") == "china"
    assert ToolInstaller._download_source("https://xafj-ct11.baidupcs.com/file/example") == "china"
    assert ToolInstaller._download_source("https://github.com/example/file") == "official"


def test_real_download_progress_records_component_source_and_bytes(tmp_path, monkeypatch):
    content = b"hello world"
    release = ToolRelease(
        "test",
        "https://github.com/example/official",
        hashlib.sha256(content).hexdigest(),
        "legendary",
        "https://1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com/download/legendary",
    )
    installer = ToolInstaller()
    monkeypatch.setattr("urllib.request.urlopen", lambda *_args, **_kwargs: Response(content))

    result = installer._download(release, tmp_path, ".progress-")

    assert result.read_bytes() == content
    status = installer.progress_status()
    assert status["component"] == "legendary"
    assert status["source"] == "official"
    assert status["downloadedBytes"] == len(content)
    assert status["progress"] == 1.0


def test_native_architecture_follows_the_system_binary_not_the_process():
    import platform

    from gamebridge.tooling import ToolInstaller

    try:
        header = Path("/bin/sh").open("rb").read(20)
    except OSError:
        header = b""
    if not header.startswith(b"\x7fELF"):
        assert ToolInstaller.native_architecture() == platform.machine().lower()
        return

    machine = int.from_bytes(header[18:20], "little")
    expected = {62: "x86_64", 183: "aarch64"}.get(machine, platform.machine().lower())
    assert ToolInstaller.native_architecture() == expected
