#!/usr/bin/env python3
"""Execute a notebook and report every cell that fails.

Unlike `jupyter nbconvert --execute`, this keeps going after a failing cell,
always writes the partially executed notebook to disk (so CI can upload it as
an artifact) and prints which cell was running when the kernel died.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError, DeadKernelError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--output", type=Path, help="where to write the executed notebook")
    parser.add_argument("--timeout", type=int, default=3600, help="per-cell timeout in seconds")
    args = parser.parse_args()

    notebook = nbformat.read(args.notebook, as_version=4)
    output = args.output or args.notebook.with_suffix(".executed.ipynb")
    output.parent.mkdir(parents=True, exist_ok=True)

    running: dict[str, int] = {}

    def on_cell_start(cell, cell_index, **kwargs):
        running["index"] = cell_index
        print(f"[cell {cell_index}] running", flush=True)

    client = NotebookClient(
        notebook,
        timeout=args.timeout,
        allow_errors=True,  # keep going, so that every failing cell is reported
        resources={"metadata": {"path": str(args.notebook.parent or ".")}},
        on_cell_start=on_cell_start,
    )

    crashed_at = None
    try:
        client.execute()
    except (DeadKernelError, CellExecutionError, RuntimeError) as exc:
        crashed_at = running.get("index")
        print(f"\nExecution aborted: {type(exc).__name__}: {exc}", flush=True)
    finally:
        nbformat.write(notebook, output)
        print(f"\nExecuted notebook written to {output}", flush=True)

    failures = []
    for index, cell in enumerate(notebook.cells):
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                failures.append((index, out))

    if failures:
        print(f"\n{len(failures)} cell(s) failed in {args.notebook}:", flush=True)
        for index, out in failures:
            source = "".join(notebook.cells[index]["source"]).strip().splitlines()
            print(f"\n--- cell {index} ---")
            for line in source[:10]:
                print(f"    {line}")
            if len(source) > 10:
                print("    ...")
            print(f"    {out['ename']}: {out['evalue']}")

    if crashed_at is not None:
        print(f"\nThe kernel died while running cell {crashed_at}.", flush=True)

    if failures or crashed_at is not None:
        return 1
    print(f"\n{args.notebook}: all cells executed without errors", flush=True)
    return 0


if __name__ == "__main__":
    code = main()
    # The notebook has already been written at this point. Leave immediately:
    # tearing down the kernel machinery can crash the interpreter (ROOT is
    # loaded in the kernel and its shutdown is not always clean), which would
    # turn a successful run into a failing one.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
