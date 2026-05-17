# Scripts directory

This directory groups script-oriented utilities and legacy operational helpers.

Use this area for:

- one-off or operator-driven generation tasks;
- report builders;
- support scripts that complement the packaged `tcria/` code;
- legacy-compatible operational entrypoints.

The intent is to keep script-style tools visually separate from the main application package while preserving the current architecture and working style.

Root-level Python should stay limited to primary application entrypoints such as `app.py` and `run_governance_pipeline.py`. New operator utilities should be added here, while reusable product logic should move into `tcria/`.
