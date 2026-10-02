import json
import os
import subprocess
from pathlib import Path


TIMEOUT_SECONDS = 10


def find_executable() -> str:
    configured_path = os.getenv("CPP_MATCHER_PATH")

    if configured_path:
        return configured_path

    project_root = Path(__file__).resolve().parents[3]
    default_path = (
        project_root
        / "matching_engine"
        / "build"
        / "matcher.exe"
    )

    return str(default_path)


def run_cpp_engine(payload: dict) -> dict:
    executable = find_executable()

    try:
        result = subprocess.run(
            [executable],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "C++ matcher timed out"
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"Could not start C++ matcher: {executable}"
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"C++ matcher failed: {result.stderr.strip()}"
        )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "C++ matcher returned invalid JSON"
        ) from exc

    if "matches" not in output:
        raise RuntimeError(
            "C++ matcher response is missing 'matches'"
        )

    return output