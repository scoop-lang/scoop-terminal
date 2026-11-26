#!/usr/bin/env python3
"""Exercise real Unix applications through the production PTY/model session, in temporary homes/configs."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = ("shell", "vim", "nvim", "less", "tmux", "kitty", "sixel", "progress")


def executable(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"required smoke application is not installed: {name}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scoop", type=Path, required=True)
    parser.add_argument("--sysroot", type=Path, required=True)
    parser.add_argument("--sixel", type=Path, help="path to img2sixel")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--term", choices=("scoop-terminal", "xterm-256color"), default="scoop-terminal")
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    args = parser.parse_args()
    if os.name == "nt":
        parser.error("this external Unix application suite requires macOS or Linux; native ConPTY tests are in demo")
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
              "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "working_tree_changes": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
              "term": args.term, "results": []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # macOS's default TMPDIR can exceed the Unix-domain socket path limit used by tmux.
    with tempfile.TemporaryDirectory(prefix="sct-", dir="/tmp") as temporary:
        folder = Path(temporary)
        source = folder / "input.txt"
        source.write_text("SMOKE_TOP\n" + "".join(f"row {i:03d}\n" for i in range(1, 120)) +
                          "SMOKE_TARGET 中 é 👩🏽‍💻\n" + "".join(f"row {i:03d}\n" for i in range(121, 200)) + "SMOKE_BOTTOM\n")
        bashrc = folder / "bashrc"
        bashrc.write_text("PS1='SMOKE_PROMPT> '\nunset PROMPT_COMMAND\nHISTFILE=/dev/null\nset -o emacs\n")
        terminfo = folder / "terminfo"
        subprocess.run([executable("tic"), "-x", "-o", str(terminfo), str(ROOT / "terminfo/scoop.terminfo")], check=True)
        environment = dict(os.environ, TERM=args.term, TERMINFO=str(terminfo), PS1="SMOKE_PROMPT> ",
                           HISTFILE=os.devnull, INPUTRC=os.devnull, TMUX_TMPDIR=str(folder))
        for name in ("TMUX", "TMUX_PANE", "LESS", "LESSOPEN", "LESSCLOSE", "VIMINIT", "EXINIT"):
            environment.pop(name, None)
        for case in args.cases:
            socket = "terminal-component-smoke"
            launcher = folder / (case + ".sh")
            if case == "sixel" and args.sixel:
                tool = str(args.sixel.expanduser().absolute())
            else:
                tool = executable({"shell": "bash", "progress": "bash", "sixel": "img2sixel"}.get(case, case))
            if case == "shell":
                command = [tool, "--noprofile", "--rcfile", str(bashrc), "-i"]
            elif case in ("vim", "nvim"):
                command = [tool, "-u", "NONE", "-i", "NONE", "-n", "+set nomore", str(source)]
                if case == "vim": command.insert(1, "-N")
            elif case == "less":
                command = [tool, "-R", "-X", str(source)]
            elif case == "kitty":
                command = kitty_command(tool)
            elif case == "sixel":
                command = [tool, str(ROOT / "terminal-ui/tests/data/images/rgba.png")]
            elif case == "tmux":
                tool = executable("tmux")
                config = folder / "tmux.conf"
                config.write_text("set -g status on\nset -g allow-passthrough on\nset -g default-terminal tmux-256color\n")
                encoded = subprocess.check_output(kitty_command(executable("kitty")), env=environment)
                stream = folder / "kitty-tmux.bin"
                stream.write_bytes(b"\x1bPtmux;" + encoded.replace(b"\x1b", b"\x1b\x1b") + b"\x1b\\")
                environment["SCOOP_TERMINAL_IMAGE_STREAM"] = str(stream)
                command = [tool, "-L", socket, "-f", str(config), "new-session", "-s", "smoke",
                           shlex.join([executable("bash"), "--noprofile", "--rcfile", str(bashrc), "-i"])]
            else:
                command = [tool, "--noprofile", "--norc", "-c", "for i in 0 10 50 100; do printf '\\r\\033[Kprogress:%s%%\\033]9;4;1;%s\\007' \"$i\" \"$i\"; sleep .02; done; printf '\\033]9;4;0\\007\\n'"]
            version = subprocess.run([tool, "-V" if case == "tmux" else "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15)
            version_text = version.stdout.splitlines()[0] if version.stdout else "unreported"
            launcher.write_text("#!/bin/sh\nset -eu\nexec " + shlex.join(command) + "\n")
            launcher.chmod(0o700)
            current = dict(environment, SCOOP_TERMINAL_SMOKE_CASE=case, SCOOP_TERMINAL_SMOKE_LAUNCHER=str(launcher))
            invocation = [str(args.scoop.expanduser().absolute()), "--sysroot", str(args.sysroot.expanduser().resolve()),
                          "test", "--release", "terminal-ui", "--ignored", "--nocapture", "--filter", "TerminalApplicationSmoke"]
            try:
                process = subprocess.run(invocation, cwd=ROOT, env=current, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
            finally:
                if case == "tmux":
                    subprocess.run([tool, "-L", socket, "kill-server"], env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if process.returncode:
                raise RuntimeError(f"{case} ({version_text}) failed:\n{process.stdout}")
            lines = [line for line in process.stdout.splitlines() if line.startswith("SMOKE ")]
            if len(lines) != 1:
                raise RuntimeError(f"{case}: expected exactly one smoke result:\n{process.stdout}")
            report["results"].append({"case": case, "version": version_text, "command": command, "result": lines[0]})
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            print(f"{case}: passed ({version_text})", flush=True)


def kitty_command(tool: str) -> list[str]:
    return [tool, "+kitten", "icat", "--transfer-mode", "stream", "--use-window-size", "80,24,640,384",
            "--stdin", "no", "--align", "left", "--passthrough", "none", str(ROOT / "terminal-ui/tests/data/images/rgba.png")]


if __name__ == "__main__":
    main()
