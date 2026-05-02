from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--cwd", default=None, help="Working directory for npx execution")
    parser.add_argument("--puppeteer-config", default=None, help="Path to puppeteer config json")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    cwd = args.cwd

    npx_path = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_path is None:
        print("ERROR\tMissing npx. Install Node.js first.")
        return 2

    cmd = [npx_path, "@mermaid-js/mermaid-cli", "-i", str(input_path), "-o", str(output_path)]
    if args.puppeteer_config:
        cmd.extend(["-p", str(Path(args.puppeteer_config))])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print("ERROR\tmmdc failed")
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        return result.returncode

    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
