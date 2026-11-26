#!/usr/bin/env python3
"""Record real terminal replies, then replay the exact bytes through the Scoop core."""

import argparse
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import select
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ESC = "\x1b"
ST = ESC + "\\"


def protocol_cases(cell_height: int) -> list[tuple[str, str]]:
    bands = max(2, (cell_height * 2 + 5) // 6)
    sixel = ESC + 'P0;1q"1;1;8;' + str(bands * 6) + "#1;2;100;0;0#1" + "-".join(["!8~"] * bands) + ST
    return [
        ("editing", ESC + "[3;5Habc中" + ESC + "[2D" + ESC + "[P"),
        ("origin-margins", ESC + "[3;12r" + ESC + "[?6h" + ESC + "[2;7H"),
        ("osc-colors", ESC + "]4;1;rgb:12/34/56" + ST + ESC + "]4;1;?\x07" +
         ESC + "]10;rgb:ab/cd/ef" + ST + ESC + "]10;?" + ST +
         ESC + "]11;rgb:01/23/45" + ST + ESC + "]11;?" + ST +
         ESC + "]12;rgb:89/ab/cd" + ST + ESC + "]12;?" + ST),
        ("synchronized-output", ESC + "[?2026$p" + ESC + "[?2026h" + "abc" +
         ESC + "[?2026$p" + ESC + "[6n" + ESC + "[?2026l" + ESC + "[?2026$p"),
        ("osc-links-commands", ESC + "]133;A" + ST + "$ " + ESC + "]133;B" + ST +
         "echo" + ESC + "]133;C" + ST + ESC + "]8;id=probe;https://example.com" + ST +
         "link中" + ESC + "]8;;" + ST + ESC + "]133;D;0" + ST),
        ("kitty-query", ESC + "_Ga=q,i=7101,f=24,s=1,v=1;/wAA" + ST),
        ("kitty-placement", ESC + "[2;3H" + ESC + "_Ga=T,i=7102,p=1,f=32,s=1,v=1,c=3,r=2;/wAA/w==" + ST +
         ESC + "[6n" + ESC + "_Ga=d,d=I,i=7102;" + ST),
        ("kitty-feature-query", ESC + "_Ga=q,i=7103,e=T,C=1,U=1,o=z,s=10,v=5;ignored" + ST),
        ("sixel-modes", ESC + "[?80$p" + ESC + "[?1070$p" + ESC + "[?8452$p"),
        ("sixel-scrolling", ESC + "[?80l" + ESC + "[?8452l" + ESC + "[2;3H" + sixel),
        ("sixel-display", ESC + "[?80h" + ESC + "[2;3H" + sixel),
        ("sixel-rightward", ESC + "[?80l" + ESC + "[?8452h" + ESC + "[2;3H" + sixel),
    ]


def exchange(payload: bytes) -> bytes:
    os.write(sys.stdout.fileno(), payload)
    output = bytearray()
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        ready, _, _ = select.select([sys.stdin.fileno()], [], [], .12 if output else .8)
        if not ready:
            break
        chunk = os.read(sys.stdin.fileno(), 65536)
        if not chunk:
            break
        output.extend(chunk)
        if len(output) > 65536:
            raise RuntimeError("unexpectedly large reference reply")
    return bytes(output)


def record(args: argparse.Namespace) -> None:
    import fcntl
    import struct
    import termios
    import tty
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("record must be the child of the reference terminal's real PTY")
    previous = termios.tcgetattr(sys.stdin.fileno())
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "terminal": args.name,
              "version": args.version, "configuration": args.configuration,
              "platform": platform.platform(), "results": []}
    try:
        tty.setraw(sys.stdin.fileno(), when=termios.TCSANOW)
        rows, columns, width, height = struct.unpack("HHHH", fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, bytes(8)))
        geometry_reply = exchange((ESC + "[16t" + ESC + "[6n").encode())
        cell = re.search(rb"\x1b\[6;(\d+);(\d+)t", geometry_reply)
        cell_height, cell_width = map(int, cell.groups()) if cell else (height // rows, width // columns)
        if min(cell_height, cell_width) <= 0:
            raise RuntimeError("reference terminal did not supply pixel geometry")
        report["geometry"] = dict(columns=columns, rows=rows, cell_width=cell_width, cell_height=cell_height,
                                  query_reply=geometry_reply.decode("utf-8"))
        for name, body in protocol_cases(cell_height):
            payload = (ESC + "c" + body + ESC + "[6n").encode()
            reply = exchange(payload)
            if not re.search(rb"\x1b\[\d+;\d+R", reply):
                raise RuntimeError(f"{name}: missing final cursor report: {reply!r}")
            report["results"].append({"case": name, "input": payload.decode(), "reply": reply.decode()})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    finally:
        os.write(sys.stdout.fileno(), (ESC + "c").encode())
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, previous)


def compare(args: argparse.Namespace) -> None:
    reports = []
    for path in args.recordings:
        source = json.loads(path.read_text())
        geometry = source["geometry"]
        fields = [str(geometry[key]) for key in ("columns", "rows", "cell_width", "cell_height")]
        fields.extend(base64.b64encode(case["input"].encode()).decode() for case in source["results"])
        environment = dict(os.environ, SCOOP_TERMINAL_REFERENCE="\n".join(fields))
        command = [str(args.scoop.expanduser().absolute()), "--sysroot", str(args.sysroot.expanduser().resolve()),
                   "test", "--release", "emulator", "--ignored", "--nocapture", "--filter", "TerminalReferenceReplay"]
        process = subprocess.run(command, cwd=ROOT, env=environment, text=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, timeout=180)
        if process.returncode:
            raise RuntimeError(process.stdout)
        replies = [base64.b64decode(line.removeprefix("REFERENCE ")).decode()
                   for line in process.stdout.splitlines() if line.startswith("REFERENCE ")]
        if len(replies) != len(source["results"]):
            raise RuntimeError("missing replay result:\n" + process.stdout)
        for case, reply in zip(source["results"], replies, strict=True):
            case["scoop_reply"] = reply
            case["identical"] = reply == case["reply"]
            print(f'{source["terminal"]}: {case["case"]}: {"identical" if case["identical"] else "different"}', flush=True)
        reports.append(source)
    report = {"scoop_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "working_tree_changes": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
              "references": reports}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    recorder = commands.add_parser("record")
    recorder.add_argument("--name", required=True)
    recorder.add_argument("--version", required=True)
    recorder.add_argument("--configuration", required=True)
    recorder.add_argument("--output", required=True, type=Path)
    comparison = commands.add_parser("compare")
    comparison.add_argument("--recordings", nargs="+", required=True, type=Path)
    comparison.add_argument("--scoop", required=True, type=Path)
    comparison.add_argument("--sysroot", required=True, type=Path)
    comparison.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    record(args) if args.command == "record" else compare(args)


if __name__ == "__main__":
    main()
