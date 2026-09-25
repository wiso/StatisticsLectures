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

    aborted = False
    crashed_at = None
    try:
        client.execute()
    except Exception as exc:  # noqa: BLE001 - whatever goes wrong, report it
        aborted = True
        # may stay None: execution can fail before the first cell starts, for
        # instance when the kernel cannot be launched at all
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
            cell = notebook.cells[index]
            source = "".join(cell["source"]).strip().splitlines()
            print(f"\n--- cell {index} ---")
            for line in source[:10]:
                print(f"    {line}")
            if len(source) > 10:
                print("    ...")
            # what the cell wrote on stderr often holds the real cause, for
            # instance the compiler errors behind a failed ROOT.gROOT.LoadMacro
            for other in cell.get("outputs", []):
                if other.get("output_type") == "stream" and other.get("name") == "stderr":
                    text = "".join(other["text"]).strip().splitlines()
                    if text:
                        print("    stderr:")
                        for line in text[:20]:
                            print(f"      {line}")
                        if len(text) > 20:
                            print("      ...")
            print(f"    {out['ename']}: {out['evalue']}")

    if aborted:
        where = f"while running cell {crashed_at}" if crashed_at is not None else "before the first cell"
        print(f"\nExecution of {args.notebook} was aborted {where}.", flush=True)

    if failures or aborted:
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
