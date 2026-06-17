"""
verify_trajectory.py — sanity-check a trajectory file without the controller.

Reads a CSV in the interface format and renders the XY path to a PNG, so you can
eyeball that the agent's output is sensible before Jinze's controller is wired in.
This is how the agent side stays demoable independently.

Usage:
    python eval/verify_trajectory.py                                  # checks interface/target_trajectory.csv
    python eval/verify_trajectory.py interface/example_trajectory.csv
"""

from __future__ import annotations
import sys
import os
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load(path):
    ts, xs, ys, zs = [], [], [], []
    with open(path) as f:
        for row in csv.DictReader(f):
            ts.append(float(row["t"])); xs.append(float(row["x"]))
            ys.append(float(row["y"])); zs.append(float(row["z"]))
    return ts, xs, ys, zs


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "interface", "target_trajectory.csv")
    if not os.path.exists(path):
        print(f"[verify] no file at {path} — run the agent first.")
        sys.exit(1)

    ts, xs, ys, zs = load(path)
    print(f"[verify] {len(ts)} waypoints, t in [{ts[0]:.2f}, {ts[-1]:.2f}] s")
    print(f"[verify] x in [{min(xs):.3f}, {max(xs):.3f}] m, "
          f"y in [{min(ys):.3f}, {max(ys):.3f}] m, z = {zs[0]:.3f} m")

    out = os.path.splitext(path)[0] + "_preview.png"
    plt.figure(figsize=(5, 5))
    plt.plot(xs, ys, "-", linewidth=2)
    plt.plot(xs[0], ys[0], "go", label="start")
    plt.plot(xs[-1], ys[-1], "rs", label="end")
    plt.gca().set_aspect("equal", "box")
    plt.grid(True); plt.legend()
    plt.xlabel("x (m)"); plt.ylabel("y (m)")
    plt.title("Target trajectory (XY)")
    plt.tight_layout(); plt.savefig(out, dpi=120)
    print(f"[verify] saved preview -> {os.path.relpath(out)}")


if __name__ == "__main__":
    main()
