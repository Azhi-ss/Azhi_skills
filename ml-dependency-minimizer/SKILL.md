---
name: ml-dependency-minimizer
description: Minimize Python/ML project dependencies to their smallest working set. Use this skill whenever the user asks to analyze, shrink, extract, or clean up dependencies for any Python or Machine Learning project — even if they just say "fix my requirements.txt", "what packages do I actually need", "extract this module from a big repo", or "set up a clean environment". Also use when migrating ML code between machines (e.g. GPU → CPU) or debugging ModuleNotFoundError in a new environment.
---

# ML Dependency Minimizer

Find the true minimal set of Python packages a project needs to run. Combines static scanning, dynamic runtime probing, and clean-environment validation.

## Bundled Resources

This skill includes executable scripts and reference docs. Use them at the indicated steps — don't reinvent the wheel.

```
ml-dependency-minimizer/
├── SKILL.md                              ← you are here
├── scripts/
│   ├── dynamic_probe.py                  ← Step 2: runtime dependency interception
│   ├── static_scan.sh                    ← Step 1: pipreqs wrapper
│   ├── merge_deps.py                     ← Step 3: combine static + dynamic results
│   └── validate_clean_env.sh             ← Step 4: clean-venv smoke test
└── references/
    └── import_name_mapping.md            ← lookup table: import name → PyPI name
```

---

## Step 1: Static Scan

Run the bundled `scripts/static_scan.sh` to scan explicit `import` statements:

```bash
bash <skill-path>/scripts/static_scan.sh /path/to/project --save /tmp/static_deps.txt
```

It auto-installs `pipreqs` if missing, handles PyPI mirror fallback, and prints a reminder that static analysis has blind spots (dynamic imports, conditional branches, framework plugins).

**When to skip this step:** If the project has no Python source files (e.g. pure config), go straight to Step 2.

---

## Step 2: Dynamic Probe

This is the core step. Run the bundled `scripts/dynamic_probe.py` to capture every package actually loaded at runtime:

```bash
python <skill-path>/scripts/dynamic_probe.py \
    --target "package.module1" "package.module2" \
    --workspace /path/to/project \
    --format pip \
    -o /tmp/dynamic_deps.txt
```

The script:
- Mocks `torch.cuda.is_available()` (and friends) so GPU-dependent code doesn't crash on CPU
- Imports each target, triggering its full dependency chain
- Diffs `sys.modules` before/after to find newly loaded packages
- Filters out stdlib and project-local files
- Translates import names to PyPI names (e.g. `PIL` → `Pillow`)

**Multiple entry points:** If the project has separate train / inference / data pipelines, pass all of them as `--target` arguments. The script unions all results automatically.

**Disabling GPU mock:** Pass `--no-gpu-mock` if the machine actually has a GPU and you want real CUDA checks.

**Before running:** Make sure the project's direct framework dependencies (torch, tensorflow, etc.) are installed in the current environment — the probe needs them to be importable so it can follow the import chain. If you're on CPU, install the CPU variant:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Step 3: Merge & Deduplicate

Run the bundled `scripts/merge_deps.py` to combine both scan results:

```bash
python <skill-path>/scripts/merge_deps.py \
    --static /tmp/static_deps.txt \
    --dynamic /tmp/dynamic_deps.txt \
    --freeze \
    -o requirements.txt
```

The script:
- Unions static + dynamic results
- Normalizes package names (handles import↔PyPI name mismatches — see `references/import_name_mapping.md` for the full mapping table)
- Detects git-hosted packages from `pip freeze` and writes them with proper `git+https://` syntax
- `--freeze` flag pins exact versions from the current environment

**When to consult the reference:** If the merge script warns about an unrecognized import name, look it up in `references/import_name_mapping.md`. That file covers ML, chemistry, and general Python ecosystems.

---

## Step 4: Validate in Clean Environment

Run the bundled `scripts/validate_clean_env.sh` to prove the requirements file is self-sufficient:

```bash
bash <skill-path>/scripts/validate_clean_env.sh \
    requirements.txt \
    "package.main_module" \
    --cpu-torch
```

The script:
- Creates a fresh `venv` in `/tmp`
- Optionally installs CPU-only PyTorch (`--cpu-torch` flag)
- Installs only what's listed in `requirements.txt`
- Attempts to `import` the target module
- Reports ✅ pass or ❌ fail with the missing package name
- Auto-cleans the temp venv

**Iterate:** If it fails, add the missing package to `requirements.txt` and re-run. Repeat until it passes.

---

## Output Format

Organize the final `requirements.txt` by purpose with comments:

```text
# Core scientific computing
numpy>=1.20
scipy>=1.7
pandas>=1.3

# ML frameworks
torch>=1.10
scikit-learn>=1.0

# Discovered via dynamic probe
lmdb>=1.2
transformers>=4.20

# Git-hosted packages
# unicore @ git+https://github.com/org/repo.git@<commit>
```

---

## Common Pitfalls

**Static ≠ dynamic results?** Trust dynamic as ground truth for what actually loads. Static catches things that *might* load in branches you didn't trigger. Use the union.

**Package appears but I never imported it?** It's a transitive dep — pip usually resolves these automatically. Only list it explicitly if it's git-hosted or needs a special install index.

**Clean-env fails despite correct list?** Check: (1) import↔PyPI name mismatch (see `references/import_name_mapping.md`), (2) system C libraries needed (`libffi-dev`, `libssl-dev`), (3) torch needs `--index-url` for CPU/GPU variants.
