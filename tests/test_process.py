import asyncio
import os
import sys
import time

import pytest

from gamebridge.process import ProcessError, SafeProcessRunner


@pytest.mark.asyncio
async def test_process_runner_preserves_argument_boundaries():
    runner = SafeProcessRunner()
    result = await runner.run(
        sys.executable,
        "-c",
        "import sys; print(sys.argv[1])",
        "value with spaces;$(ignored)",
    )
    assert result.stdout.strip() == "value with spaces;$(ignored)"


@pytest.mark.asyncio
async def test_process_runner_reports_failure():
    runner = SafeProcessRunner()
    with pytest.raises(ProcessError):
        await runner.run(sys.executable, "-c", "raise SystemExit(7)")


@pytest.mark.asyncio
async def test_process_runner_redacts_sensitive_arguments_and_output():
    runner = SafeProcessRunner()
    sensitive_value = "authorization-" + "code-must-not-leak"
    result = await runner.run(
        sys.executable,
        "-c",
        "import sys; print(sys.argv[1])",
        sensitive_value,
        sensitive_arguments=frozenset({2}),
    )
    assert sensitive_value not in repr(result)
    assert result.argv[-1] == "<redacted>"
    assert result.stdout.strip() == "<redacted>"


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_process_runner_allows_a_longer_window_for_one_bounded_command():
    runner = SafeProcessRunner(timeout=0.2)
    with pytest.raises(TimeoutError, match="after 0.2s"):
        await runner.run(sys.executable, "-c", "import time; time.sleep(3); print('late')")

    result = await runner.run(
        sys.executable,
        "-c",
        "import time; time.sleep(0.4); print('slow but allowed')",
        timeout=5,
    )
    assert result.stdout.strip() == "slow but allowed"


@pytest.mark.asyncio
async def test_process_runner_allows_a_larger_limit_for_one_bounded_command():
    runner = SafeProcessRunner(output_limit=4)
    with pytest.raises(RuntimeError, match="command output exceeded safety limit"):
        await runner.run(sys.executable, "-c", "print('12345')")

    result = await runner.run(
        sys.executable,
        "-c",
        "print('12345')",
        output_limit=16,
    )
    assert result.stdout.strip() == "12345"
@pytest.mark.asyncio
async def test_process_error_keeps_the_tail_of_a_long_failure():
    runner = SafeProcessRunner()
    marker = "root-cause-on-the-last-line"
    program = (
        "import sys; sys.stderr.write('noise ' * 4000); sys.stderr.write('" + marker + "')"
        "; raise SystemExit(4)"
    )

    with pytest.raises(ProcessError) as raised:
        await runner.run(sys.executable, "-c", program)

    assert str(raised.value).endswith(marker)

def _write_spawner(tmp_path):
    """A command that starts its own long-lived worker, like Legendary does."""
    marker = tmp_path / "worker.pid"
    script = tmp_path / "spawner.py"
    script.write_text(
        "import subprocess, sys, time\n"
        "worker = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        f"open({str(marker)!r}, 'w').write(str(worker.pid))\n"
        "time.sleep(60)\n",
        encoding="utf-8",
    )
    return script, marker


def _assert_worker_gone(marker):
    pid = int(marker.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)
    raise AssertionError("the worker survived and keeps running")


@pytest.mark.asyncio
async def test_process_runner_timeout_stops_the_tools_own_workers(tmp_path):
    script, marker = _write_spawner(tmp_path)
    runner = SafeProcessRunner()

    with pytest.raises(TimeoutError, match="timed out"):
        await runner.run(sys.executable, str(script), timeout=1)

    _assert_worker_gone(marker)


@pytest.mark.asyncio
async def test_process_runner_cancellation_stops_the_tools_own_workers(tmp_path):
    script, marker = _write_spawner(tmp_path)
    runner = SafeProcessRunner()
    task = asyncio.create_task(runner.run(sys.executable, str(script), timeout=60))
    await asyncio.sleep(0.6)

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    _assert_worker_gone(marker)
