# control/  — Nonlinear MPC controller (owner: Jinze Lyu)

The NMPC controller that tracks a target trajectory on the 6-DoF AR4 arm.

## What goes here
Your existing thesis controller (MATLAB), with one change: instead of a hard-coded
`p_ref`, **read `p_ref` from the interface file** `../interface/target_trajectory.csv`
(columns `t,x,y,z`, meters/seconds, robot base frame — see `../interface/INTERFACE.md`).

Everything else stays as-is: the receding-horizon NMPC, joint-velocity limits, and your
existing logging/validation. Your output (joint-velocity log, end-effector path) is unchanged.

## M1 goal
Read an external trajectory from the interface file and track it in simulation.
A good first commit: a script that loads the CSV into `p_ref` and runs your existing loop.
