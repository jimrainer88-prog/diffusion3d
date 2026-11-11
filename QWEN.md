# Rules for the coding agent (diffusion3d)

- Read PLAN.md first. Work on ONE step only: the one the user names.
- Do not rewrite PLAN.md or QWEN.md unless the user asks.
- Do not run installs, downloads, model inference, tests or Docker builds. Write the files; the user runs them and pastes errors back.
- For TripoSR and TRELLIS.2, use their official README APIs from third_party/. If unsure of a function name, say so instead of guessing.
- Python 3.11, type hints, argparse CLIs, paths relative to the project root.
- Don't create files in data/ or third_party/ except .gitkeep.
- No dependencies beyond requirements.txt without asking.
- When a step is finished, list the files you changed and the "Done" check from PLAN.md the user should run.
