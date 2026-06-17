"""
agent.py — first-version LLM agent.

Turns a natural-language instruction into a typed Trajectory (see interface/trajectory.py),
then writes it to the CSV the controller reads (interface/target_trajectory.csv).

Two modes:
  1. LLM mode: if ANTHROPIC_API_KEY is set, the agent asks Claude to choose a shape and
     parameters, returning structured JSON we validate into a Trajectory.
  2. Fallback mode: if no key is set, a small rule-based parser handles a few shapes
     ("figure-eight", "circle", "line to x y", "go to x y") so the pipeline runs end-to-end
     offline. This keeps M2 demoable without depending on network/keys.

Usage:
    python agent/agent.py "trace a figure eight"
    python agent/agent.py "move the end-effector to 0.1 -0.5"
"""

from __future__ import annotations
import sys
import os
import json
import math
import re

# make interface/ importable when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "interface"))
from trajectory import Trajectory, Waypoint  # noqa: E402

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "interface", "target_trajectory.csv")

# Workspace defaults (robot base frame), aligned with the controller's setup.
Z = 0.47          # constant working height (m)
Y_CENTER = -0.60  # in front of the base (m)
DT = 0.05         # seconds between waypoints


# ---------- shape generators (return a Trajectory) ----------

def figure_eight(A: float = 0.1, periods: float = 1.0) -> Trajectory:
    wx, wy = 0.24 * math.pi, 0.12 * math.pi
    T = (2 * math.pi / wy) * periods
    n = int(round(T / DT))
    wps = []
    for k in range(n + 1):
        t = k * DT
        wps.append(Waypoint(t=t, x=A * math.sin(wx * t), y=A * math.sin(wy * t) + Y_CENTER, z=Z))
    return Trajectory(waypoints=wps)


def circle(R: float = 0.08, periods: float = 1.0) -> Trajectory:
    w = 0.2 * math.pi
    T = (2 * math.pi / w) * periods
    n = int(round(T / DT))
    wps = []
    for k in range(n + 1):
        t = k * DT
        wps.append(Waypoint(t=t, x=R * math.cos(w * t), y=R * math.sin(w * t) + Y_CENTER, z=Z))
    return Trajectory(waypoints=wps)


def line_to(x: float, y: float, seconds: float = 3.0, x0: float = 0.0, y0: float = Y_CENTER) -> Trajectory:
    n = int(round(seconds / DT))
    wps = []
    for k in range(n + 1):
        s = k / n
        t = k * DT
        wps.append(Waypoint(t=t, x=x0 + s * (x - x0), y=y0 + s * (y - y0), z=Z))
    return Trajectory(waypoints=wps)


# ---------- fallback (offline) parser ----------

def fallback_plan(instruction: str) -> Trajectory:
    s = instruction.lower()
    nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", s)]
    if "eight" in s or "figure-8" in s or "figure 8" in s:
        return figure_eight()
    if "circle" in s or "loop" in s or "round" in s:
        return circle()
    if ("go to" in s or "move" in s or "line" in s) and len(nums) >= 2:
        return line_to(nums[0], nums[1])
    # default: a gentle figure-eight so the pipeline always produces something
    return figure_eight(A=0.08)


# ---------- LLM planner (Claude) ----------

PLANNER_SYSTEM = """You convert a natural-language robot instruction into a motion plan.
Respond with ONLY a JSON object, no prose, no markdown. Schema:
{"shape": one of ["figure_eight","circle","line_to"],
 "A": float (amplitude in meters, optional, for figure_eight),
 "R": float (radius in meters, optional, for circle),
 "x": float (target x in meters, required for line_to),
 "y": float (target y in meters, required for line_to)}
Workspace is small: amplitudes/radii around 0.05-0.12 m, targets within x in [-0.15,0.15], y in [-0.75,-0.45]."""


def llm_plan(instruction: str) -> Trajectory:
    import anthropic  # imported lazily so fallback mode needs no dependency
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=PLANNER_SYSTEM,
        messages=[{"role": "user", "content": instruction}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
    text = text.replace("```json", "").replace("```", "").strip()
    spec = json.loads(text)
    shape = spec.get("shape")
    if shape == "figure_eight":
        return figure_eight(A=float(spec.get("A", 0.1)))
    if shape == "circle":
        return circle(R=float(spec.get("R", 0.08)))
    if shape == "line_to":
        return line_to(float(spec["x"]), float(spec["y"]))
    raise ValueError(f"unknown shape from planner: {shape}")


# ---------- entrypoint ----------

def plan(instruction: str) -> Trajectory:
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return llm_plan(instruction)
        except Exception as e:
            print(f"[agent] LLM planning failed ({e}); using offline fallback.")
    return fallback_plan(instruction)


def main():
    instruction = " ".join(sys.argv[1:]) or "trace a figure eight"
    traj = plan(instruction)
    traj.save_csv(OUT_PATH)
    print(f'[agent] instruction: "{instruction}"')
    print(f"[agent] wrote {len(traj.waypoints)} waypoints -> {os.path.relpath(OUT_PATH)}")


if __name__ == "__main__":
    main()
