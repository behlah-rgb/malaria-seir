# Project: SEIR-Vector Malaria Model with Urban Drainage Index

## What this is
Academic project. 8-compartment ODE model (A_v, S_v, E_v, I_v, S_h, E_h, I_h, R_h).
The professor-approved math is in docs/SPEC.md. That file is the source of truth.

## Rules
- NEVER change an equation, parameter definition, or formula from SPEC.md without asking me first.
- If you think the spec has a numerical problem, STOP and explain it. Propose a fix,
  wait for my approval, and mark every approved deviation with a comment `# DEVIATION:`
  and a line in docs/DEVIATIONS.md.
- Only edit files inside this project folder.
- Install packages only via pip inside .venv, and add them to requirements.txt.
- Use odeint from scipy.integrate. Time unit is days. Rainfall is mm/day, temperature °C.
- Keep every function documented with units in its docstring.
- Every parameter value must live in one place (params.py) with a comment on its source
  or "PLACEHOLDER - needs literature value".
- Run `pytest` after changes and report results.
- Explain what you changed in plain language, I am a student and must understand the code.

## Style
Modular, type hints, no giant functions, no hard-coded numbers inside equations.

## Session workflow

### Start of every session
- Read docs/PROGRESS.md and docs/DEVIATIONS.md before doing anything else.
- Summarize in 3-4 lines where the project stands and what the next step is,
  then wait for my instruction.

### Deviations from the spec (strict)
- If a task requires departing from docs/SPEC.md (clamping, domain guards, handling
  division by zero, changing a formula, changing a definition), STOP and ask me first.
  Do not implement the deviation until I approve it.
- Once approved, do ALL THREE of the following in the same task:
  1. Mark the code with a comment: `# DEVIATION: <short reason>, see DEVIATIONS.md #N`
  2. Append an entry to docs/DEVIATIONS.md with: number, date, file and function,
     the original spec formula, what the code does instead, the reason, and
     "approved by: user".
  3. Mention it in the end-of-task summary.
- Before finishing any task, run `grep -rn "DEVIATION:" src/` and confirm every match
  has a matching entry in docs/DEVIATIONS.md. Fix any mismatch.
- Never delete or rewrite old entries in DEVIATIONS.md. If a deviation is later
  reversed, add a new entry saying so.

### End of every task
Update docs/PROGRESS.md: files changed, why, test results, unfinished items, next step.
Add decisions (initial conditions, parameter choices, etc.) under "Decisions" with the reason.
Append new entries with the date. Do not restate equations; point to docs/SPEC.md instead.

### Keeping PROGRESS.md small (automatic trimming)
- After updating PROGRESS.md, run `wc -l docs/PROGRESS.md`.
- If it exceeds 150 lines, trim it immediately, without waiting for me to ask:
  1. Move the oldest "Change log" entries into docs/archive/PROGRESS_ARCHIVE.md
     (append only, never delete), keeping the most recent 10 entries in PROGRESS.md.
  2. Condense older "Decisions" into one line each, keeping the decision and the reason.
     Keep full detail only for decisions that still affect the code.
  3. Remove any completed items from "Next step" and "Open questions".
  4. Never remove: current status, unresolved open questions, or active decisions.
- Never trim or archive DEVIATIONS.md. It is a permanent record.
- After trimming, tell me in one line what was archived and the new line count.

### Commits
- Never commit unless I ask. When I do, write a short title plus 2-3 lines explaining why.