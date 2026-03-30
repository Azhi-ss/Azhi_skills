#!/usr/bin/env python3
"""
Dynamic Dependency Probe — Generic Template

Intercepts all modules loaded at runtime via sys.modules diffing.
Automatically mocks GPU availability so ML projects don't crash on CPU-only
machines during the probing phase.

Usage:
    # Probe a single entry point
    python dynamic_probe.py --target "mypackage.train" --workspace /path/to/project

    # Probe multiple entry points (union of all deps)
    python dynamic_probe.py \
        --target "mypackage.train" "mypackage.inference" "mypackage.data" \
        --workspace /path/to/project

    # Output as pip-installable list
    python dynamic_probe.py --target "mypackage" --workspace . --format pip

    # Save results to file
    python dynamic_probe.py --target "mypackage" --workspace . -o deps.txt
"""

import sys
import os
import argparse
import sysconfig
import importlib
from typing import Set, List


# ============================================================================
# Import-name → PyPI-name mapping for common packages
# ============================================================================
IMPORT_TO_PYPI = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "yaml": "PyYAML",
    "sklearn": "scikit-learn",
    "attr": "attrs",
    "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "git": "GitPython",
    "google": "protobuf",
    "lxml": "lxml",
    "wx": "wxPython",
    "serial": "pyserial",
    "usb": "pyusb",
    "skimage": "scikit-image",
    "Bio": "biopython",
    "Crypto": "pycryptodome",
}


def get_external_packages(new_modules: Set[str], workspace: str) -> List[str]:
    """
    Filter a set of module names down to only external (site-packages) ones.
    Excludes stdlib, builtins, and project-local packages.
    """
    workspace_abs = os.path.abspath(workspace)
    external = []

    for mod_name in sorted(new_modules):
        # Skip internal/private modules
        if mod_name.startswith("_"):
            continue

        # Skip builtins
        if mod_name in sys.builtin_module_names:
            continue

        try:
            mod = sys.modules.get(mod_name) or importlib.import_module(mod_name)
        except Exception:
            continue

        mod_file = getattr(mod, "__file__", None)
        if mod_file is None:
            continue

        mod_file_abs = os.path.abspath(mod_file)

        # Skip project-local files
        if mod_file_abs.startswith(workspace_abs):
            continue

        # Keep only site-packages / dist-packages / conda packages
        if any(marker in mod_file for marker in ("site-packages", "dist-packages")):
            external.append(mod_name)
        elif "conda" in mod_file.lower() and ("envs" in mod_file or "pkgs" in mod_file):
            external.append(mod_name)

    return external


def apply_gpu_mocks():
    """
    Patch torch CUDA functions so that imports don't crash on CPU machines.
    Returns a list of mock context managers to clean up later.
    """
    mocks = []
    try:
        from unittest.mock import patch

        # Only apply if torch is available
        try:
            import torch  # noqa: F401
            mocks.append(patch("torch.cuda.is_available", return_value=True))
            mocks.append(patch("torch.cuda.device_count", return_value=1))
            mocks.append(patch("torch.cuda.current_device", return_value=0))
            mocks.append(patch("torch.cuda.get_device_name", return_value="Mock GPU"))
            for m in mocks:
                m.start()
        except ImportError:
            pass  # No torch, no mocking needed
    except Exception:
        pass
    return mocks


def probe_targets(targets: List[str], workspace: str) -> Set[str]:
    """
    Import each target module and return the set of top-level package names
    that were newly loaded.
    """
    # Ensure workspace is on sys.path
    workspace_abs = os.path.abspath(workspace)
    if workspace_abs not in sys.path:
        sys.path.insert(0, workspace_abs)

    # Also add common sub-paths (src/, lib/)
    for subdir in ("src", "lib"):
        sub_path = os.path.join(workspace_abs, subdir)
        if os.path.isdir(sub_path) and sub_path not in sys.path:
            sys.path.insert(0, sub_path)

    before = set(sys.modules.keys())

    for target in targets:
        try:
            __import__(target)
            print(f"  ✓ Successfully imported: {target}")
        except Exception as e:
            print(f"  ✗ Import failed for {target}: {type(e).__name__}: {e}")
            print(f"    (This is OK — partial imports still register dependencies)")

    after = set(sys.modules.keys())
    new_modules = after - before

    # Extract top-level package names
    top_level = set()
    for mod_name in new_modules:
        base = mod_name.split(".")[0]
        if not base.startswith("_"):
            top_level.add(base)

    return top_level


def format_output(packages: List[str], fmt: str) -> List[str]:
    """Format package names for output."""
    if fmt == "pip":
        return [IMPORT_TO_PYPI.get(pkg, pkg) for pkg in packages]
    return packages  # "raw" format


def main():
    parser = argparse.ArgumentParser(
        description="Dynamically probe Python/ML project dependencies via sys.modules interception.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dynamic_probe.py --target mypackage --workspace .
  python dynamic_probe.py --target mypackage.train mypackage.infer --workspace /project
  python dynamic_probe.py --target mypackage --workspace . --format pip -o requirements_dynamic.txt
        """,
    )
    parser.add_argument(
        "--target", nargs="+", required=True,
        help="Module(s) to import, e.g. 'mypackage.train' 'mypackage.model'",
    )
    parser.add_argument(
        "--workspace", default=".",
        help="Project root directory (added to sys.path). Default: current dir.",
    )
    parser.add_argument(
        "--format", choices=["raw", "pip"], default="raw",
        help="Output format. 'raw' = import names, 'pip' = PyPI package names. Default: raw.",
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="Write results to file instead of stdout.",
    )
    parser.add_argument(
        "--no-gpu-mock", action="store_true",
        help="Disable automatic GPU mocking.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Dynamic Dependency Probe")
    print("=" * 60)
    print(f"Workspace : {os.path.abspath(args.workspace)}")
    print(f"Targets   : {', '.join(args.target)}")
    print(f"GPU Mock  : {'disabled' if args.no_gpu_mock else 'enabled'}")
    print()

    # Apply GPU mocks
    mocks = []
    if not args.no_gpu_mock:
        print("[1/3] Applying GPU mocks...")
        mocks = apply_gpu_mocks()

    # Probe
    print("[2/3] Importing targets...")
    top_level = probe_targets(args.target, args.workspace)

    # Filter to external
    print("[3/3] Filtering to external packages...")
    external = get_external_packages(top_level, args.workspace)
    formatted = format_output(external, args.format)

    # Cleanup mocks
    for m in mocks:
        try:
            m.stop()
        except Exception:
            pass

    # Output
    print()
    print("-" * 60)
    print(f"Found {len(formatted)} external dependencies:")
    print("-" * 60)

    for pkg in formatted:
        print(f"  {pkg}")

    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(formatted) + "\n")
        print(f"\nSaved to: {args.output}")

    print()
    return formatted


if __name__ == "__main__":
    main()
