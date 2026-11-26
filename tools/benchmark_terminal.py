#!/usr/bin/env python3
"""Run opt-in release benchmarks, with runtime allocation/RSS metrics and an optional Git baseline."""

import argparse
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ("ascii120", "ascii240", "sgr120", "sgr240", "unicode120", "unicode240", "history100k", "reflow10k")
VIEWS = ("paint120x1", "paint120x2", "paint240x1", "paint240x2")


def run_case(root: Path, args, label: str, case: str) -> dict:
    environment = dict(os.environ, SCOOP_GC_STATS="1")
    cone = "terminal-ui" if case in VIEWS else "emulator"
    command = [str(args.scoop), "--sysroot", str(args.sysroot), "test", "--release",
               str(root / cone), "--ignored", "--nocapture", "--filter", case]
    process = subprocess.run(command, cwd=root, env=environment, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    text = process.stdout + "\n" + process.stderr
    if process.returncode:
        raise RuntimeError(f"{label}/{case} failed:\n{text}")
    records = []
    metrics = []
    for line in text.splitlines():
        if line.startswith("BENCH "):
            record = dict(item.split("=", 1) for item in line[6:].split())
            records.append({key: int(value) if key != "name" else value for key, value in record.items()})
        if line.startswith('{"scoop_gc":'):
            metrics.append(json.loads(line))
    if len(records) != 1 or len(metrics) != 1:
        raise RuntimeError(f"{label}/{case}: expected one benchmark and one process metric record:\n{text}")
    result = {"label": label, "case": case, **records[0], "runtime": metrics[0]}
    print(f"{label}/{case}: {result['ns'] / 1e6:.2f} ms, "
          f"p95 {result['p95'] / 1e6:.3f} ms, "
          f"allocated {metrics[0]['allocated_bytes'] / 1048576:.1f} MiB, "
          f"peak RSS {metrics[0]['peak_rss_bytes'] / 1048576:.1f} MiB", flush=True)
    return result


def export_baseline(destination: Path, reference: str) -> None:
    archive = subprocess.check_output(["git", "archive", reference, "emulator", "terminal-ui", "demo", "Cone.toml"], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        files.extractall(destination, filter="data")
    benchmark = (ROOT / "emulator/tests/benchmarks.scoop").read_text()
    # d990f72 predates explicit Terminal.close; the measured feed/lookup loops are identical.
    start = benchmark.index("private fun closeCoreBenchmark")
    benchmark = benchmark[:start] + "private fun closeCoreBenchmark(terminal: Terminal) {}\n"
    (destination / "emulator/tests/benchmarks.scoop").write_text(benchmark)
    manifest = destination / "emulator/Cone.toml"
    text = manifest.read_text()
    if '"scoop:scoop.platform"' not in text:
        text = text.replace("[test-dependencies]", '[test-dependencies]\n"scoop:scoop.platform" = "0.1.0"')
    manifest.write_text(text)
    view = (ROOT / "terminal-ui/tests/benchmarks.scoop").read_text()
    view = view.replace('frame.shape([], "")', 'frame.shape(None, "")')
    view = view[:view.index("private fun prepareViewBenchmark")] + """private fun prepareViewBenchmark(terminal: Terminal, appearance: TerminalAppearance) {}
private fun closeViewBenchmark(terminal: Terminal) {}
private fun viewBenchmarkFrame(
    terminal: Terminal, appearance: TerminalAppearance, cache: TerminalGlyphCache,
    size: Size, columns: Long, rows: Long, scale: Long, revision: Long
): TerminalFrame {
    val geometry = GridGeometry(
        size, cache.metrics, terminal.historySize, terminal.lines(terminal.historySize, rows),
        columns, rows, terminal.screenRevision, true
    )
    return TerminalFrame(geometry, revision, terminal.cursor, 0L, appearance, cache)
}
"""
    (destination / "terminal-ui/tests/benchmarks.scoop").write_text(view)
    fonts = destination / "terminal-ui/tests/data"
    fonts.mkdir(exist_ok=True)
    for name in ("FiraCode-Regular.ttf", "FiraCode-LICENSE.txt"):
        shutil.copyfile(ROOT / "terminal-ui/tests/data" / name, fonts / name)
    # The old cache lacks a counter. Instrument cache misses without changing lookup/shaping.
    glyphs = destination / "terminal-ui/src/glyphs.scoop"
    text = glyphs.read_text().replace("    private var references = 1L", "    private var references = 1L\n    var shapeCount = 0L")
    text = text.replace("        layouts[key] = value", "        shapeCount += 1L\n        layouts[key] = value")
    glyphs.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scoop", type=Path, required=True)
    parser.add_argument("--sysroot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="raw JSON report outside the repository")
    parser.add_argument("--label", default="working")
    parser.add_argument("--baseline", choices=("d990f72",), help="fixed design baseline with documented API-only adapters")
    parser.add_argument("--cases", nargs="+", choices=CORE + VIEWS, default=list(CORE + VIEWS))
    parser.add_argument("--repetitions", type=int, default=1)
    args = parser.parse_args()
    # The installed launcher selects its command by executable name; preserve its symlink path.
    args.scoop = args.scoop.expanduser().absolute()
    args.sysroot = args.sysroot.expanduser().resolve()
    args.output = args.output.expanduser().resolve()
    if args.repetitions < 1:
        parser.error("repetitions must be positive")
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "machine": platform.machine(),
              "platform": platform.platform(), "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "toolchain": subprocess.check_output([str(args.scoop), "--version"], text=True).strip(), "results": []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scoop-terminal-baseline-") as temporary:
        roots = [(args.label, ROOT)]
        if args.baseline:
            baseline = Path(temporary)
            export_baseline(baseline, args.baseline)
            roots.insert(0, (args.baseline, baseline))
        for label, root in roots:
            for case in args.cases:
                for iteration in range(args.repetitions):
                    result = run_case(root, args, label, case)
                    result["iteration"] = iteration + 1
                    report["results"].append(result)
                    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
