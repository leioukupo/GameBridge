from __future__ import annotations

import hashlib
import fcntl
import os
import platform
import shutil
import subprocess
import ssl
import tarfile
import tempfile
import threading
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

ALLOWED_DOWNLOAD_HOSTS = {
    "github.com",
    "objects.githubusercontent.com",
    "release-assets.githubusercontent.com",
    "1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com",
}
MAX_TOOL_SIZE = 200 * 1024 * 1024
MAX_COMPATIBILITY_TOOL_SIZE = 700 * 1024 * 1024
SYSTEM_CA_FILES = (
    "/etc/ssl/cert.pem",
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/pki/tls/certs/ca-bundle.crt",
)


@dataclass(frozen=True, slots=True)
class ToolRelease:
    version: str
    url: str
    sha256: str
    component: str = ""
    gateway_url: str | None = None


LEGENDARY_RELEASES = {
    "x86_64": ToolRelease(
        "0.21.0",
        "https://github.com/legendary-gl/legendary/releases/download/0.21.0/legendary_linux_x64",
        "c83d1595a9e2cbae4e66b69ecaa1f8649da99b617a72f93312d342e6a5a799c7",
        "legendary",
        "https://1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com/download/legendary",
    ),
    "aarch64": ToolRelease(
        "0.21.0",
        "https://github.com/legendary-gl/legendary/releases/download/0.21.0/legendary_linux_arm64",
        "ed0a523c7310aec590a0da9ecdada185fc3b02e75fa5148c0e7ef0680095dce5",
        "legendary",
    ),
}

UMU_RELEASE = ToolRelease(
    "1.4.0",
    "https://github.com/Open-Wine-Components/umu-launcher/releases/download/1.4.0/"
    "umu-launcher-1.4.0-zipapp.tar",
    "138ce4b8843608a257d4bee88191ca78a989778bcefd8abb3c1d1aaac3ac6fb8",
    "umu",
    "https://1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com/download/umu",
)

DWPROTON_RELEASE = ToolRelease(
    "dwproton-11.0-11-x86_64",
    "https://dawn.wine/dawn-winery/dwproton/releases/download/"
    "dwproton-11.0-11/dwproton-11.0-11-x86_64.tar.xz",
    "94e502e935e3d743e33647f580489ebd3b54b0789196d87b066f06456455a8dd7"
    "966f149dfcb73e64e9d345a6f2c20ac4b24a9095cad643577b34ae45dcefff5",
    "dwproton",
    "https://1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com/download/dw",
)

GE_PROTON_RELEASE = ToolRelease(
    "GE-Proton11-5-x86_64",
    "https://github.com/GloriousEggroll/proton-ge-custom/releases/download/"
    "GE-Proton11-5/GE-Proton11-5-x86_64.tar.gz",
    "8fb1f3ae65a8dc22efd8099ff489075f0eebddf01c445b423244589f6f0a1e19"
    "c01de5d1e722b97fc1ebaf6390c813052ed55290058f8d21f1353a36146f4a2c",
    "geproton",
    "https://1300823591-fyjwaget5r.ap-guangzhou.tencentscf.com/download/ge",
)


class ToolInstaller:
    def __init__(self) -> None:
        self._progress_lock = threading.Lock()
        self._progress: dict[str, Any] = {
            "active": False,
            "component": None,
            "phase": "idle",
            "progress": 0.0,
            "source": None,
            "downloadedBytes": 0,
            "totalBytes": None,
        }

    def progress_status(self) -> dict[str, Any]:
        with self._progress_lock:
            return dict(self._progress)

    def set_progress(self, **values: Any) -> None:
        with self._progress_lock:
            self._progress.update(values)

    @staticmethod
    def native_architecture() -> str:
        """Architecture the operating system itself runs.

        An emulated plugin host reports its guest architecture, but the game
        client starts game processes outside that host. Reading the ELF header
        of a system binary answers the question without asking this process.
        """
        for candidate in (Path("/bin/sh"), Path("/usr/bin/env")):
            try:
                with candidate.open("rb") as handle:
                    header = handle.read(20)
            except OSError:
                continue
            if not header.startswith(b"\x7fELF") or len(header) < 20:
                continue
            machine = int.from_bytes(header[18:20], "little")
            if machine == 0x3E:
                return "x86_64"
            if machine == 0xB7:
                return "aarch64"
            break
        return platform.machine().lower()

    def supports_managed_compatibility_tools(self) -> bool:
        """GameBridge's GE-Proton and DWProton archives are x86_64 only."""
        return self.native_architecture() in {"x86_64", "amd64"}

    @staticmethod
    def child_architecture() -> str:
        """Architecture that downloaded command-line tools actually run as.

        A plugin host can itself be emulated: an x86_64 Decky host running
        under FEX on an aarch64 machine starts its children in that same
        translated mode, so a child still reports x86_64. Asking a child keeps
        the downloaded build matched to the interpreter that loads its native
        helper modules, which is the value that matters on a native aarch64
        host as well.
        """
        uname = shutil.which("uname")
        machine = ""
        if uname is not None:
            try:
                completed = subprocess.run(  # noqa: S603 - fixed helper path from PATH
                    [uname, "-m"],
                    capture_output=True,
                    check=True,
                    text=True,
                    timeout=5,
                )
                machine = completed.stdout.strip().lower()
            except (OSError, subprocess.SubprocessError):
                machine = ""
        if not machine:
            machine = platform.machine().lower()
        aliases = {"amd64": "x86_64", "arm64": "aarch64"}
        return aliases.get(machine, machine)

    def legendary_release(self) -> ToolRelease:
        architecture = self.child_architecture()
        try:
            return LEGENDARY_RELEASES[architecture]
        except KeyError as exc:
            raise RuntimeError(f"unsupported architecture: {architecture}") from exc

    def install_legendary(self, target: str | Path) -> dict[str, str]:
        release = self.legendary_release()
        target_path = Path(target).expanduser().resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._download(release, target_path.parent, ".legendary-")
        try:
            self.set_progress(active=True, phase="installing", progress=1.0)
            temporary_path.chmod(0o755)
            os.replace(temporary_path, target_path)
            self.set_progress(active=False, phase="complete", progress=1.0)
        except BaseException:
            self.set_progress(active=False, phase="failed")
            raise
        finally:
            temporary_path.unlink(missing_ok=True)
        return {"version": release.version, "path": os.fspath(target_path)}

    def install_umu(self, target: str | Path) -> dict[str, str]:
        target_path = Path(target).expanduser().resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        release = UMU_RELEASE
        archive = self._download(release, target_path.parent, ".umu-")
        staged = target_path.with_name(f".{target_path.name}.new")
        try:
            self.set_progress(active=True, phase="installing", progress=1.0)
            with tarfile.open(archive, "r:") as bundle:
                member = bundle.getmember("umu/umu-run")
                if not member.isfile() or member.size > 10 * 1024 * 1024:
                    raise RuntimeError("UMU release does not contain a valid zipapp")
                source = bundle.extractfile(member)
                if source is None:
                    raise RuntimeError("UMU zipapp could not be extracted")
                with staged.open("wb") as destination:
                    while chunk := source.read(1024 * 1024):
                        destination.write(chunk)
                    destination.flush()
                    os.fsync(destination.fileno())
            staged.chmod(0o755)
            os.replace(staged, target_path)
            self.set_progress(active=False, phase="complete", progress=1.0)
        except BaseException:
            self.set_progress(active=False, phase="failed")
            raise
        finally:
            archive.unlink(missing_ok=True)
            staged.unlink(missing_ok=True)
        return {"version": release.version, "path": os.fspath(target_path)}

    def install_compatibility_tool(
        self, release: ToolRelease, destination_root: str | Path
    ) -> dict[str, str]:
        if not self.supports_managed_compatibility_tools():
            raise RuntimeError("managed compatibility tools require x86_64")
        root = Path(destination_root).expanduser().resolve()
        target = root / release.version
        proton = target / "proton"
        if proton.is_file() and os.access(proton, os.X_OK):
            return {"version": release.version, "path": os.fspath(target)}
        root.mkdir(parents=True, exist_ok=True)
        lock_path = root / f".{release.version}.gamebridge.lock"
        with lock_path.open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if proton.is_file() and os.access(proton, os.X_OK):
                return {"version": release.version, "path": os.fspath(target)}
            if shutil.disk_usage(root).free < 4 * 1024**3:
                raise RuntimeError("insufficient space for compatibility tool")
            archive = self._download(
                release,
                root,
                ".gamebridge-compat-",
                max_size=MAX_COMPATIBILITY_TOOL_SIZE,
                algorithm="sha512",
            )
            staged_parent = Path(tempfile.mkdtemp(prefix=".gamebridge-stage-", dir=root))
            try:
                self.set_progress(active=True, phase="installing", progress=1.0)
                with tarfile.open(archive, "r:*") as bundle:
                    members = bundle.getmembers()
                    self._validate_archive_members(members)
                    bundle.extractall(staged_parent, members=members, filter="fully_trusted")
                candidates = [
                    item
                    for item in staged_parent.iterdir()
                    if item.is_dir() and (item / "proton").is_file()
                ]
                if len(candidates) != 1:
                    raise RuntimeError("compatibility archive has an unexpected layout")
                staged = candidates[0]
                if staged.name != release.version:
                    raise RuntimeError("compatibility archive version does not match release")
                (staged / "proton").chmod((staged / "proton").stat().st_mode | 0o111)
                if target.exists():
                    raise RuntimeError("incomplete compatibility tool already exists")
                os.replace(staged, target)
                self.set_progress(active=False, phase="complete", progress=1.0)
            except BaseException:
                self.set_progress(active=False, phase="failed")
                raise
            finally:
                archive.unlink(missing_ok=True)
                shutil.rmtree(staged_parent, ignore_errors=True)
        return {"version": release.version, "path": os.fspath(target)}

    def _download(
        self,
        release: ToolRelease,
        directory: Path,
        prefix: str,
        *,
        max_size: int = MAX_TOOL_SIZE,
        algorithm: str = "sha256",
    ) -> Path:
        routes = [url for url in (release.gateway_url, release.url) if url]
        for url in routes:
            self._validate_url(url)
        # The regional gateway can be temporarily unavailable while the
        # upstream release asset is healthy. Every managed component keeps its
        # official URL as a second route, so a gateway outage cannot block an
        # Epic sign-in or a compatibility runtime install. Both routes are
        # checked against the same pinned digest.
        last_error: Exception = RuntimeError(f"no download route for {release.component}")
        for url in routes:
            try:
                return self._download_from(
                    url, release, directory, prefix, max_size=max_size, algorithm=algorithm
                )
            except (OSError, RuntimeError) as exc:
                last_error = exc
        raise last_error

    def _download_from(
        self,
        url: str,
        release: ToolRelease,
        directory: Path,
        prefix: str,
        *,
        max_size: int,
        algorithm: str,
    ) -> Path:
        self.set_progress(
            active=True,
            component=release.component or release.version,
            phase="connecting",
            progress=0.0,
            source=None,
            downloadedBytes=0,
            totalBytes=None,
        )
        request = urllib.request.Request(  # noqa: S310 -- URL is allowlisted by the caller
            url,
            headers={"User-Agent": "GameBridge/0.18 (+https://github.com/Open-Wine-Components)"},
        )
        descriptor, temporary_name = tempfile.mkstemp(prefix=prefix, dir=directory)
        temporary_path = Path(temporary_name)
        digest = hashlib.new(algorithm)
        size = 0
        try:
            with os.fdopen(descriptor, "wb") as destination:
                with urllib.request.urlopen(  # noqa: S310
                    request, timeout=30, context=self._ssl_context()
                ) as response:
                    final_url = response.geturl()
                    self._validate_url(final_url)
                    source = self._download_source(final_url)
                    declared_size = int(response.headers.get("Content-Length", "0") or 0)
                    if declared_size > max_size:
                        raise RuntimeError("tool download is unexpectedly large")
                    self.set_progress(
                        active=True,
                        phase="downloading",
                        progress=0.0,
                        source=source,
                        totalBytes=declared_size or None,
                    )
                    while chunk := response.read(1024 * 1024):
                        size += len(chunk)
                        if size > max_size:
                            raise RuntimeError("tool download exceeded size limit")
                        digest.update(chunk)
                        destination.write(chunk)
                        self.set_progress(
                            active=True,
                            phase="downloading",
                            progress=min(0.99, size / declared_size) if declared_size else 0.0,
                            source=source,
                            downloadedBytes=size,
                            totalBytes=declared_size or None,
                        )
                destination.flush()
                os.fsync(destination.fileno())
            self.set_progress(active=True, phase="verifying", progress=1.0)
            if digest.hexdigest() != release.sha256:
                raise RuntimeError("tool SHA-256 verification failed")
            return temporary_path
        except BaseException:
            self.set_progress(active=False, phase="failed")
            temporary_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def _download_source(url: str) -> str:
        hostname = (urlparse(url).hostname or "").casefold()
        return "china" if (
            hostname.endswith(".baidupcs.com")
            or hostname.endswith(".pcs.baidu.com")
        ) else "official"

    @staticmethod
    def _validate_archive_members(members: list[tarfile.TarInfo]) -> None:
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise RuntimeError("compatibility archive contains an unsafe path")
            if member.isdev() or member.isfifo():
                raise RuntimeError("compatibility archive contains a special file")
            if member.issym() or member.islnk():
                link = PurePosixPath(member.linkname)
                if link.is_absolute():
                    raise RuntimeError("compatibility archive contains an unsafe link")
                combined = (path.parent / link) if member.issym() else link
                normalized: list[str] = []
                for part in combined.parts:
                    if part in {"", "."}:
                        continue
                    if part == "..":
                        if len(normalized) <= 1:
                            raise RuntimeError(
                                "compatibility archive contains an unsafe link"
                            )
                        normalized.pop()
                    else:
                        normalized.append(part)
                if not normalized or normalized[0] != path.parts[0]:
                    raise RuntimeError("compatibility archive contains an unsafe link")

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlparse(url)
        allowed_hosts = {
            *ALLOWED_DOWNLOAD_HOSTS,
            "dawn.wine",
            "eu-west-1.euronodes.com",
        }
        hostname = (parsed.hostname or "").casefold()
        baidu_download_host = (
            hostname.endswith(".baidupcs.com")
            or hostname.endswith(".pcs.baidu.com")
        )
        if parsed.scheme != "https" or (
            hostname not in allowed_hosts and not baidu_download_host
        ):
            raise ValueError("download URL is not allowlisted")

    @staticmethod
    def _ssl_context() -> ssl.SSLContext:
        for candidate in SYSTEM_CA_FILES:
            if Path(candidate).is_file():
                return ssl.create_default_context(cafile=candidate)
        raise RuntimeError("SteamOS system CA certificate bundle was not found")
