# language-controlled-manipulation

An LLM agent that turns natural-language instructions into robot-arm trajectories, executed by a nonlinear MPC (NMPC) controller in simulation. **No hardware required.**

You say *"trace a figure-eight"* or *"move the end-effector to (0.1, −0.5)"*; an LLM agent plans the task and emits a **typed trajectory**; the NMPC controller tracks it on a 6-DoF AR4 arm in simulation.

This is a hands-on implementation of the **language-to-action (VLA)** paradigm — inspired by work like SayCan and RT-style policies — built as a learning project with clean, separable module ownership.

---

## Architecture

```
 natural-language          LLM AGENT                 typed              NMPC CONTROLLER            arm tracks
   instruction      →   (plan + tool-calls)   →   trajectory    →    (6-DoF AR4, sim)      →    the trajectory
                         [ agent/ ]              [ interface/ ]       [ control/ + sim/ ]
```

The two halves meet at **one typed interface** (`interface/`): the agent writes a trajectory file, the controller reads it. Because the contract is fixed, each side is developed and committed independently.

---

## Module ownership

| Module        | Owner            | What it does                                                        |
|---------------|------------------|---------------------------------------------------------------------|
| `agent/`      | Rui (Ray) Sun    | LLM agent: parse instruction → plan → emit a typed trajectory        |
| `eval/`       | Rui (Ray) Sun    | Evaluation harness: success rate over an instruction suite           |
| `interface/`  | Rui (Ray) Sun    | The typed trajectory contract (schema + spec + example)              |
| `control/`    | Jinze Lyu        | Nonlinear MPC controller (6-DoF AR4) that tracks a target trajectory |
| `sim/`        | Jinze Lyu        | Simulation / validation environment (MATLAB)                         |

Each contributor commits their own modules; commit history reflects who built what.

---

## How it fits together (the interface)

The agent produces a **reference trajectory** — a time-stamped sequence of task-space points — and writes it to a file. The controller reads that file and tracks it. See [`interface/INTERFACE.md`](interface/INTERFACE.md) for the exact format, units, and a worked example (`interface/example_trajectory.csv`).

---

## Milestones

- **M1 — Controller accepts an external target.** The NMPC controller reads a target trajectory from the interface (instead of a hard-coded one) and tracks it in sim. *(Jinze)*
- **M2 — Natural language → a single target.** The agent turns one instruction into a valid trajectory file; the controller executes it. First language-driven motion. *(Rui leads; first integration)*
- **M3 — Multi-step + eval.** The agent decomposes a compound instruction into an ordered sequence of targets; an eval harness measures success rate over an instruction suite. **This is the complete-project version.** *(Rui)*
- **M4 — (Optional) Object-aware via vision.** Targets come from detected object positions rather than hard-coded coordinates. *(Jinze-weighted, optional)*

---

## Repo layout

```
agent/        # LLM agent: instruction → typed trajectory  (Rui)
interface/    # the typed trajectory contract + example      (Rui)
eval/         # evaluation harness                           (Rui)
control/      # nonlinear MPC controller                     (Jinze)
sim/          # simulation / validation                      (Jinze)
```

## Status

Early development. Built by [Rui (Ray) Sun](https://github.com/rayruisun) and Jinze Lyu.
