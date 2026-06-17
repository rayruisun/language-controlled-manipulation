# Trajectory Interface Contract

This is the single contract between the **agent** (Rui) and the **controller** (Jinze).
The agent writes a trajectory file in this format; the controller reads it and tracks it.
As long as both sides honor this contract, the two halves can be developed independently.

---

## File format

A reference trajectory is a **CSV file** with a header row and one row per timestep.

### Columns

| Column | Unit    | Description                                          |
|--------|---------|------------------------------------------------------|
| `t`    | seconds | Timestamp of this waypoint (monotonically increasing)|
| `x`    | meters  | End-effector target X position (task space)          |
| `y`    | meters  | End-effector target Y position (task space)          |
| `z`    | meters  | End-effector target Z position (task space)          |

### Conventions

- **Coordinate frame:** robot base frame. X forward, Y left, Z up. (Same frame the controller's forward kinematics already use.)
- **Units:** meters for position, seconds for time. (Not millimeters.)
- **Sampling:** timesteps should be evenly spaced (e.g. `dt = 0.05 s`), but the controller should tolerate minor irregularity.
- **Length:** any number of rows ≥ 2.
- **Encoding:** UTF-8, comma-separated, with the header row exactly as named above.

### Example

```
t,x,y,z
0.00,0.000,-0.600,0.470
0.05,0.012,-0.598,0.470
0.10,0.024,-0.596,0.470
...
```

See [`example_trajectory.csv`](example_trajectory.csv) for a full, runnable example (a figure-eight).

---

## Who writes / reads what

- **Agent (Rui)** → *writes* this file. Given a natural-language instruction, the agent plans and emits a trajectory in exactly this format.
- **Controller (Jinze)** → *reads* this file. Replace the hard-coded `p_ref` in the NMPC loop with "read `p_ref` from this CSV," then track it as usual. The controller's existing output (joint-velocity log, end-effector path) stays the same.

---

## Default file location

By convention the agent writes to:

```
interface/target_trajectory.csv
```

and the controller reads from the same path. (Configurable on both sides, but this is the default both sides assume.)

---

## Versioning

If the format changes (e.g. we add orientation or gripper columns later), bump the version note here and update both sides together. Current version: **v1 (position-only, x/y/z over time).**

Possible future additions (not in v1): `qw,qx,qy,qz` orientation, a `gripper` open/close flag, or per-waypoint velocity.
