#!/usr/bin/env python3
"""Create a timestamped Totem prototype validation evidence bundle.

This helper does not claim physical PASS/FAIL outcomes. It captures reproducible host/Pi
command output and creates an IN_PROGRESS evidence record for operator observations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STAGES = {
    "pre-power",
    "bench-display",
    "bench-audio",
    "bench-controls",
    "bench-led",
    "pre-enclosure-burnin",
    "enclosure-fit",
    "enclosure-burnin",
    "final",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_name(value: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "-" for c in value)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_capture(bundle: Path, name: str, command: list[str]) -> dict:
    out = bundle / f"{safe_name(name)}.txt"
    executable = shutil.which(command[0])
    if executable is None:
        text = f"SKIPPED: executable not found: {command[0]}\n"
        rc = None
    else:
        proc = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        text = proc.stdout
        rc = proc.returncode
    out.write_text(text, encoding="utf-8")
    return {
        "path": out.name,
        "kind": "command-output",
        "sha256": sha256(out),
        "source_command": " ".join(command),
        "return_code": rc,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=sorted(STAGES), default="pre-power")
    parser.add_argument("--output", default="validation/evidence")
    parser.add_argument("--totem-repo", default=os.environ.get("TOTEM_REPO"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        assert safe_name("a b/c") == "a-b-c"
        assert "pre-power" in STAGES
        print("capture.py self-test PASS")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"prototype-v1-{stamp}-{args.stage}"
    bundle = Path(args.output) / run_id
    bundle.mkdir(parents=True, exist_ok=False)

    artifacts = []
    artifacts.append(run_capture(bundle, "uname", ["uname", "-a"]))
    artifacts.append(run_capture(bundle, "os-release", ["cat", "/etc/os-release"]))
    artifacts.append(run_capture(bundle, "vcgencmd-throttled", ["vcgencmd", "get_throttled"]))
    artifacts.append(run_capture(bundle, "vcgencmd-temperature", ["vcgencmd", "measure_temp"]))
    artifacts.append(run_capture(bundle, "systemctl-totem", ["systemctl", "status", "totem.service", "--no-pager"]))
    artifacts.append(run_capture(bundle, "journal-totem", ["journalctl", "-u", "totem.service", "-n", "250", "--no-pager"]))

    totem_revision = None
    if args.totem_repo:
        repo = Path(args.totem_repo)
        if (repo / ".git").exists():
            rev = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
            if rev.returncode == 0:
                totem_revision = rev.stdout.strip()
            pnpm = shutil.which("pnpm")
            if pnpm:
                artifacts.append(run_capture(bundle, "totem-validate-pi", [pnpm, "--dir", str(repo), "validate:pi"]))

    record_artifacts = [
        {k: v for k, v in artifact.items() if k in {"path", "kind", "sha256", "source_command"}}
        for artifact in artifacts
    ]
    record = {
        "schema_version": "1.0",
        "run_id": run_id,
        "started_at": now_iso(),
        "completed_at": None,
        "stage": args.stage,
        "scope": {"generic_public": True, "private_cosmetic": False},
        "hardware_revision": None,
        "measurement_record": None,
        "cad_revision": None,
        "totem_revision": totem_revision,
        "operator": None,
        "results": [],
        "artifacts": record_artifacts,
        "overall_status": "IN_PROGRESS",
    }
    record_path = bundle / "evidence.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    meta = bundle / "capture-meta.txt"
    meta.write_text(
        f"captured_at={now_iso()}\npython={sys.version.split()[0]}\nplatform={platform.platform()}\n",
        encoding="utf-8",
    )
    print(bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
