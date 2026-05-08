#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import getpass

ROOT = Path(".")
SIM_DIR_PATTERN = "chroma_*/sims/chroma_*_eldens_*"

OUT_OK_RE = re.compile(
    r"^\s*(?:"
    r"Submitted batch job \d+"
    r"|simulation exited"
    r")\s*$"
)

ERR_OK_RE = re.compile(
    r"^\s*/usr/bin/bash: warning: setlocale: LC_ALL: cannot change locale \(en_US\.UTF-8\)\s*$"
)


def get_running_jobids() -> set[int]:
    user = getpass.getuser()

    try:
        result = subprocess.run(
            ["squeue", "-u", user, "-h", "-o", "%A"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as exc:
        print(f"Warning: could not read squeue jobs: {exc}")
        return set()

    jobids = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            jobids.add(int(line))

    return jobids


def job_number(path: Path) -> int | None:
    match = re.fullmatch(r"(\d+)\.(out|err)", path.name)
    return int(match.group(1)) if match else None


running_jobids = get_running_jobids()

for sim_dir in sorted(ROOT.glob(SIM_DIR_PATTERN)):
    if not sim_dir.is_dir():
        continue

    nums = {
        job_number(p)
        for p in sim_dir.iterdir()
        if p.is_file() and job_number(p) is not None
    }

    nums = {
        n for n in nums
        if (sim_dir / f"{n}.out").exists()
        and (sim_dir / f"{n}.err").exists()
    }

    if not nums:
        continue

    latest = max(nums)

    # Skip jobs that are currently in the queue/running.
    if latest in running_jobids:
        continue

    out_path = sim_dir / f"{latest}.out"
    err_path = sim_dir / f"{latest}.err"

    out_text = out_path.read_text(errors="replace")
    err_text = err_path.read_text(errors="replace")

    out_bad = OUT_OK_RE.fullmatch(out_text) is None
    err_bad = ERR_OK_RE.fullmatch(err_text) is None

    if out_bad or err_bad:
        print("=" * 100)
        print(sim_dir)
        print(f"Latest job: {latest}")

        if out_bad:
            print(f"\n--- {out_path.name} ---")
            print(out_text.rstrip())

        if err_bad:
            print(f"\n--- {err_path.name} ---")
            print(err_text.rstrip())
