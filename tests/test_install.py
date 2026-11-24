import asyncio

import pytest

import gamebridge.application as application_module
from gamebridge.application import GameBridgeApplication
from gamebridge.database import Database
from gamebridge.install import EpicInstallManager
from gamebridge.jobs import InstallJobStore
from gamebridge.models import JobState
from gamebridge.providers.epic import EpicProvider
from gamebridge.storage import StorageRoot


@pytest.mark.asyncio
async def test_install_dialog_lists_storage_when_sizes_are_unreadable(tmp_path, monkeypatch):
    """A stalled Epic size lookup must not hide the writable storage locations."""
    application = GameBridgeApplication(tmp_path)
    application.start()
    with application.database.connect() as db:
        db.execute(
            "INSERT INTO catalog_games(id,title,normalized_title) VALUES(?,?,?)",
            ("epic:size-test", "Size Test", "size test"),
        )
        db.execute(
            "INSERT INTO game_releases"
            "(canonical_game_id,provider_id,external_game_id,region,release_channel) "
            "VALUES(?,?,?,?,?)",
            ("epic:size-test", "epic", "size-app", "global", "stable"),
        )
    provider = application.providers.get("epic")
    assert isinstance(provider, EpicProvider)
    monkeypatch.setattr(provider, "executable", lambda: None)
    monkeypatch.setattr(
        application_module,
        "storage_roots",
        lambda: [StorageRoot(tmp_path, "/dev/root", True)],
    )

    result = await application.storage_locations("epic:size-test")

    assert result["sizes_available"] is False
    assert result["sizes_reason"] == "legendary.not_installed"
    assert result["required_bytes"] == 0
    assert [item["path"] for item in result["locations"]] == [
        str(tmp_path / "Games" / "GameBridge" / "Epic")
    ]
    assert result["locations"][0]["enough_space"] is True
    assert result["recommended_id"] == result["locations"][0]["id"]


def test_second_epic_download_is_refused_while_one_is_running(tmp_path):
    """Two Legendary writers would overwrite each other’s install records."""
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    running = jobs.create("epic", "first-game", {"installRoot": str(tmp_path / "first")})

    class Provider:
        pass

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="install.another_running"):
        manager.start("second-game", "Second Game", tmp_path / "second")

    assert [job.id for job in jobs.active()] == [running.id]


def test_a_paused_epic_download_still_holds_the_slot(tmp_path, monkeypatch):
    """A paused Legendary is a suspended writer, so it can still overwrite records."""
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    paused = jobs.create("epic", "first-game", {"installRoot": str(tmp_path / "first")})
    jobs.transition(paused.id, JobState.PAUSED)

    class Provider:
        pass

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]
    monkeypatch.setattr("gamebridge.install.approved_install_path", lambda candidate: True)

    with pytest.raises(ValueError, match="install.another_running"):
        manager.start("second-game", "Second Game", tmp_path / "second")

    assert [job.external_game_id for job in jobs.active()] == ["first-game"]


@pytest.mark.asyncio
async def test_a_failed_epic_download_does_not_hold_the_slot(tmp_path, monkeypatch):
    """A retryable failure stays resumable but must not block another install."""
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    failed = jobs.create("epic", "first-game", {"installRoot": str(tmp_path / "first")})
    jobs.transition(failed.id, JobState.VALIDATING)
    jobs.fail(failed.id, "network dropped", retryable=True)

    class Provider:
        pass

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]
    monkeypatch.setattr("gamebridge.install.approved_install_path", lambda candidate: True)
    started: list[str] = []

    async def fake_run(
        job_id, app_name, install_root, *, resume_existing=False, operation="install"
    ):
        started.append(app_name)

    monkeypatch.setattr(manager, "_run", fake_run)
    job_id = manager.start("second-game", "Second Game", tmp_path / "second")
    await manager.tasks[job_id]

    assert started == ["second-game"]


def test_install_records_lost_during_a_download_are_written_back(tmp_path):
    class Provider:
        def __init__(self) -> None:
            self.written: dict[str, object] | None = None

        def retained_installations(self):
            return {"second": {"install_path": "/games/second", "executable": "s.exe"}}

        def restore_retained_installations(self, payload) -> None:
            self.written = payload

    database = Database(tmp_path / "jobs.db")
    database.initialize()
    provider = Provider()
    manager = EpicInstallManager(provider, InstallJobStore(database))  # type: ignore[arg-type]

    manager._restore_lost_installations({"first": {"install_path": "/games/first", "executable": "f.exe"}})

    assert provider.written == {
        "second": {"install_path": "/games/second", "executable": "s.exe"},
        "first": {"install_path": "/games/first", "executable": "f.exe"},
    }


def test_intact_install_records_are_left_alone(tmp_path):
    calls: list[object] = []

    class Provider:
        def retained_installations(self):
            return {"first": {"install_path": "/games/first", "executable": "f.exe"}}

        def restore_retained_installations(self, payload) -> None:
            calls.append(payload)

    database = Database(tmp_path / "jobs.db")
    database.initialize()
    manager = EpicInstallManager(Provider(), InstallJobStore(database))  # type: ignore[arg-type]

    manager._restore_lost_installations({"first": {"install_path": "/games/first", "executable": "f.exe"}})

    assert calls == []


def test_legendary_progress_lines_update_persistent_job(tmp_path):
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    job = jobs.create("epic", "sample", {"phase": "starting"})

    class Provider:
        pass

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]
    manager._consume_line(job.id, "= Progress: 42.50% (42/100), ETA: 00:01:23")
    manager._consume_line(job.id, " - Downloaded: 512.25 MiB, Written: 600.00 MiB")
    manager._consume_line(job.id, " + Download - 12.75 MiB/s (raw)")
    updated = jobs.get(job.id)
    assert updated.progress == 0.425
    assert updated.payload["eta"] == "00:01:23"
    assert updated.payload["downloadedMiB"] == 512.25
    assert updated.payload["speedMiBs"] == 12.75


@pytest.mark.asyncio
async def test_paused_job_restarts_after_plugin_reload(tmp_path, monkeypatch):
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    job = jobs.create(
        "epic",
        "hogwarts",
        {"installRoot": str(tmp_path / "games"), "resumeState": "downloading_game"},
    )
    jobs.transition(job.id, JobState.PAUSED)

    class Provider:
        pass

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]
    called = asyncio.Event()

    async def fake_run(
        job_id, app_name, install_root, *, resume_existing=False, operation="install"
    ):
        assert job_id == job.id
        assert app_name == "hogwarts"
        assert install_root == (tmp_path / "games").resolve()
        assert resume_existing is True
        assert operation == "install"
        called.set()

    monkeypatch.setattr(manager, "_run", fake_run)
    manager.resume(job.id)
    await asyncio.wait_for(called.wait(), timeout=1)
    await manager.tasks[job.id]


def test_interrupted_job_becomes_resumable_after_reload(tmp_path):
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    job = jobs.create("epic", "sample", {"installRoot": str(tmp_path / "games")})
    jobs.transition(job.id, JobState.VALIDATING)

    class Provider:
        pass

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]
    manager.recover_interrupted_jobs()
    recovered = jobs.get(job.id)
    assert recovered.state == JobState.PAUSED
    assert recovered.payload["resumeState"] == "downloading_game"


@pytest.mark.asyncio
async def test_stop_game_cancels_orphaned_paused_record(tmp_path):
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    job = jobs.create("epic", "sample", {"installRoot": str(tmp_path / "games")})
    jobs.transition(job.id, JobState.PAUSED)

    class Provider:
        @staticmethod
        def executable():
            return None

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]
    await manager.stop_game("sample")
    assert jobs.get(job.id).state == JobState.CANCELLED


class _FakeOutput:
    def __init__(self, lines):
        self._lines = iter(lines)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._lines)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class _FakeProcess:
    pid = 4242

    def __init__(self, lines, return_code=0):
        self.stdout = _FakeOutput(lines)
        self.returncode = return_code

    async def wait(self):
        return self.returncode


@pytest.mark.asyncio
async def test_isolated_update_simulation_runs_update_and_completes(tmp_path, monkeypatch):
    """Exercise the whole update state machine without touching a real game."""
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    job = jobs.create(
        "epic",
        "sample",
        {
            "installRoot": str(tmp_path / "games"),
            "operation": "update",
            "phase": "install.preparing",
        },
    )

    class Provider:
        updated = []

        @staticmethod
        def executable():
            return tmp_path / "legendary"

        @staticmethod
        def environment():
            return {}

        @staticmethod
        def is_installed(app_name):
            return app_name == "sample"

        def mark_updated(self, app_name):
            self.updated.append(app_name)

        @staticmethod
        def retained_installations():
            return {}

        @staticmethod
        def restore_retained_installations(payload):
            raise AssertionError("nothing to restore here")

    provider = Provider()
    manager = EpicInstallManager(provider, jobs)  # type: ignore[arg-type]
    invoked = []

    async def fake_stop(*_args):
        return None

    async def fake_subprocess(*args, **_kwargs):
        invoked.append(args)
        return _FakeProcess(
            [
                b"= Progress: 37.50% (3/8), ETA: 00:00:12\n",
                b" - Downloaded: 128.00 MiB, Written: 150.00 MiB\n",
            ]
        )

    monkeypatch.setattr(manager, "_stop_orphaned_install", fake_stop)
    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_subprocess)

    await manager._run(job.id, "sample", tmp_path / "games", operation="update")

    assert invoked
    command = invoked[0]
    assert command[1:4] == ("-y", "update", "sample")
    assert "--base-path" not in command
    assert provider.updated == ["sample"]
    completed = jobs.get(job.id)
    assert completed.state == JobState.COMPLETED
    assert completed.payload["downloadedMiB"] == 128.0


@pytest.mark.asyncio
async def test_paused_update_resumes_as_update_after_plugin_reload(tmp_path, monkeypatch):
    database = Database(tmp_path / "jobs.db")
    database.initialize()
    jobs = InstallJobStore(database)
    job = jobs.create(
        "epic",
        "sample",
        {
            "installRoot": str(tmp_path / "games"),
            "resumeState": "downloading_game",
            "operation": "update",
        },
    )
    jobs.transition(job.id, JobState.PAUSED)

    class Provider:
        pass

    manager = EpicInstallManager(Provider(), jobs)  # type: ignore[arg-type]
    called = asyncio.Event()

    async def fake_run(
        job_id, app_name, install_root, *, resume_existing=False, operation="install"
    ):
        assert job_id == job.id
        assert app_name == "sample"
        assert install_root == (tmp_path / "games").resolve()
        assert resume_existing is True
        assert operation == "update"
        called.set()

    monkeypatch.setattr(manager, "_run", fake_run)
    manager.resume(job.id)
    await asyncio.wait_for(called.wait(), timeout=1)
    await manager.tasks[job.id]
