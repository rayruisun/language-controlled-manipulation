"""
Typed trajectory schema — the code form of interface/INTERFACE.md.

The agent produces a Trajectory; we serialize it to the CSV the controller reads.
Keeping the contract as a Pydantic model means the agent can't emit a malformed
trajectory without failing loudly here.
"""

from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, field_validator


class Waypoint(BaseModel):
    """A single task-space target at a given time."""
    t: float = Field(..., description="Timestamp in seconds (monotonically increasing).")
    x: float = Field(..., description="End-effector X in meters (robot base frame).")
    y: float = Field(..., description="End-effector Y in meters.")
    z: float = Field(..., description="End-effector Z in meters.")


class Trajectory(BaseModel):
    """A reference trajectory: an ordered list of task-space waypoints."""
    waypoints: List[Waypoint] = Field(..., min_length=2)

    @field_validator("waypoints")
    @classmethod
    def _times_increase(cls, wps: List[Waypoint]) -> List[Waypoint]:
        for a, b in zip(wps, wps[1:]):
            if b.t <= a.t:
                raise ValueError(f"timestamps must strictly increase (got {a.t} then {b.t})")
        return wps

    def to_csv(self) -> str:
        lines = ["t,x,y,z"]
        for w in self.waypoints:
            lines.append(f"{w.t:.2f},{w.x:.4f},{w.y:.4f},{w.z:.4f}")
        return "\n".join(lines) + "\n"

    def save_csv(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_csv())
