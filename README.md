# composer-system

This repository models historically grounded composers as **structured creative identities** stored in JSON and validated against a shared schema. It is a small Python library for loading profiles, deriving structured reflections, and assembling creative-concept scaffolding from that data.

## What this repo is

- Data-first composer profiles with explicit separation of impression, depth, personality, artistic identity, musical style, and creative process  
- Schema-backed validation (Pydantic models with an exportable JSON Schema)  
- Safe loading (path confinement, filename-to-id checks)  
- Deterministic helpers that derive prompts and briefs **only** from profile fields  

## What this repo is not

- Not an agent runtime, tool executor, orchestration layer, or workflow engine  
- Not a control plane and **not** part of Jarvis HUD, OpenClaw, or similar stacks  
- Not a substitute for musicology: interpretive fields should be labeled and kept cautious in `source_notes`  

## Current composers

Shipped example profiles live in `data/composers/`:

- `bach.json`  
- `beethoven.json`  
- `chopin.json`  
- `mozart.json`  

Add new files as `{id}.json` where `id` matches the `id` field inside the JSON.

## Setup and tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Schema export

The canonical schema is defined in code (`composer_system/models.py`). Export JSON Schema for editors and external validators:

```bash
python -c "from composer_system.validate import profile_json_schema; open('schemas/composer_profile.v1.json','w').write(profile_json_schema())"
```

Re-run this after any model change so `schemas/composer_profile.v1.json` stays in sync.

## Adding a new composer safely

1. Copy an existing file in `data/composers/` and rename it to `{slug}.json`.  
2. Set `id` to the same slug (lowercase, no path segments).  
3. Fill `public_impression` and `deeper_dimensions` without reducing the figure to a single cartoon trait.  
4. Use `source_notes` to separate **well-attested facts** (dates, places, surviving sources) from **interpretive modeling**.  
5. Run `pytest` so `tests/test_profiles.py` catches duplicates, empty `source_notes`, and shallow caricature phrasing.  

## License

Add a license if you plan to publish the repo publicly.
