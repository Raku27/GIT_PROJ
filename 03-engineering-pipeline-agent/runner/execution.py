"""POSIX command execution with deadlines, process-group cleanup and bounded logs."""

import os
import selectors
import signal
import subprocess
from time import monotonic

LOG_LIMIT_BYTES = (
    1024 * 1024
)  # Per stream per stage; additional output is drained and discarded.


def _kill_group(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def execute(stage, project_dir, run_dir):
    start = monotonic()
    result = {
        "status": "failed",
        "returncode": None,
        "execution_time": 0.0,
        "error": None,
        "logs_truncated": False,
        "stdout_log": stage["name"] + ".stdout.log",
        "stderr_log": stage["name"] + ".stderr.log",
    }
    argv = [arg.replace("{run_dir}", str(run_dir)) for arg in stage["argv"]]
    result["argv"] = argv
    process = None
    selector = selectors.DefaultSelector()
    try:
        with (run_dir / result["stdout_log"]).open("wb") as stdout_log, (
            run_dir / result["stderr_log"]
        ).open("wb") as stderr_log:
            try:
                process = subprocess.Popen(
                    argv,
                    cwd=project_dir,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )
            except OSError as exc:
                result["error"] = "Unable to start command: " + str(exc)
                return result
            for pipe, log in (
                (process.stdout, stdout_log),
                (process.stderr, stderr_log),
            ):
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, [log, 0])
            deadline = start + stage["timeout_seconds"]
            drain_deadline = None
            timed_out = False
            while selector.get_map() or process.poll() is None:
                now = monotonic()
                if drain_deadline is None:
                    if process.poll() is not None:
                        # Finite stages may not leave background children holding pipes open.
                        _kill_group(process)
                        drain_deadline = now + 0.5
                    elif now >= deadline:
                        timed_out = True
                        _kill_group(process)
                        drain_deadline = now + 0.5
                if drain_deadline is not None and now >= drain_deadline:
                    break
                for key, _ in selector.select(0.05):
                    try:
                        chunk = os.read(key.fd, 65536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                        continue
                    log, written = key.data
                    remaining = max(0, LOG_LIMIT_BYTES - written)
                    log.write(chunk[:remaining])
                    key.data[1] += min(len(chunk), remaining)
                    if len(chunk) > remaining:
                        result["logs_truncated"] = True
            result["returncode"] = process.wait(timeout=1)
            if timed_out:
                result["error"] = "Command exceeded timeout_seconds"
            elif result["returncode"] != 0:
                result["error"] = "Command exited with status " + str(
                    result["returncode"]
                )
            else:
                result["status"] = "success"
    finally:
        if process is not None:
            _kill_group(process)
            process.wait(timeout=1)
            for pipe in (process.stdout, process.stderr):
                if pipe is not None and not pipe.closed:
                    pipe.close()
        selector.close()
        result["execution_time"] = monotonic() - start
    return result
