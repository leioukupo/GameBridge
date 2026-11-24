import sys

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
