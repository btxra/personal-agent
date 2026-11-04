from pathlib import Path
import os

import sync_origin_main as engine

original_emit = engine.emit
original_read_input = engine.read_input


def emit(payload: dict) -> None:
    context = payload.get("additional_context")
    original_emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}} if context else {})


def read_input() -> dict:
    event = original_read_input()
    event["hook_event_name"] = "sessionStart"
    return event


def workspace_root(event: dict) -> Path:
    root = os.environ.get("DEVIN_PROJECT_DIR")
    return Path(root) if root else Path.cwd()


engine.emit = emit
engine.read_input = read_input
engine.workspace_root = workspace_root

if __name__ == "__main__":
    try:
        raise SystemExit(engine.main())
    except Exception as exc:
        emit({"additional_context": f"personal-agent git sync: aborted ({type(exc).__name__})"})
        raise SystemExit(0)
