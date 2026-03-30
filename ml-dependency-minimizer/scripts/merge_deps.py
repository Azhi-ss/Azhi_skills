#!/usr/bin/env python3
"""
Merge & Deduplicate — Combine static + dynamic scan results into one clean list.

Usage:
    python merge_deps.py --static static_deps.txt --dynamic dynamic_deps.txt -o requirements.txt
    python merge_deps.py --static static_deps.txt --dynamic dynamic_deps.txt --freeze  # also capture versions
"""

import argparse
import subprocess
import re
import sys
from typing import Dict, Set


# ============================================================================
# Import-name → PyPI-name mapping
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
    "skimage": "scikit-image",
    "Bio": "biopython",
    "Crypto": "pycryptodome",
    "serial": "pyserial",
    "usb": "pyusb",
    "wx": "wxPython",
    "lxml": "lxml",
    "gi": "PyGObject",
    "socks": "PySocks",
}

# Reverse mapping for dedup
PYPI_TO_IMPORT = {v.lower(): k for k, v in IMPORT_TO_PYPI.items()}


def parse_requirements_file(path: str) -> Set[str]:
    """Parse a requirements file, return set of normalized package names."""
    packages = set()
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Strip version specifiers: numpy>=1.20 -> numpy
                name = re.split(r"[><=!~;\[]", line)[0].strip()
                if name:
                    packages.add(name.lower())
    except FileNotFoundError:
        print(f"Warning: File not found: {path}", file=sys.stderr)
    return packages


def get_pip_freeze() -> Dict[str, str]:
    """Get {package_name_lower: 'package==version'} from pip freeze."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True, text=True
    )
    freeze_map = {}
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-e"):
            continue
        name = re.split(r"[><=!~@]", line)[0].strip()
        if name:
            freeze_map[name.lower()] = line
    return freeze_map


def get_git_packages() -> Dict[str, str]:
    """Find packages installed from git repos."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True, text=True
    )
    git_pkgs = {}
    for line in result.stdout.strip().split("\n"):
        if "git+" in line or "@" in line:
            name = re.split(r"[><=!~@\s]", line)[0].strip()
            if name:
                git_pkgs[name.lower()] = line.strip()
    return git_pkgs


def normalize_name(name: str) -> str:
    """Normalize to PyPI package name."""
    return IMPORT_TO_PYPI.get(name, name)


def main():
    parser = argparse.ArgumentParser(description="Merge static + dynamic dependency lists.")
    parser.add_argument("--static", required=True, help="Path to static scan output (pipreqs)")
    parser.add_argument("--dynamic", required=True, help="Path to dynamic probe output")
    parser.add_argument("-o", "--output", default="requirements.txt", help="Output file (default: requirements.txt)")
    parser.add_argument("--freeze", action="store_true", help="Pin versions from current pip freeze")
    args = parser.parse_args()

    print("Merging dependency lists...")
    print(f"  Static : {args.static}")
    print(f"  Dynamic: {args.dynamic}")

    static_pkgs = parse_requirements_file(args.static)
    dynamic_pkgs = parse_requirements_file(args.dynamic)

    # Union and normalize
    all_pkgs = set()
    for pkg in static_pkgs | dynamic_pkgs:
        normalized = normalize_name(pkg).lower()
        all_pkgs.add(normalized)

    # Remove known non-packages
    skip = {"__future__", "builtins", "antigravity", "this", "typing_extensions"}
    all_pkgs -= skip

    print(f"\n  Static found  : {len(static_pkgs)} packages")
    print(f"  Dynamic found : {len(dynamic_pkgs)} packages")
    print(f"  Dynamic-only  : {len(dynamic_pkgs - static_pkgs)} (missed by static)")
    print(f"  Merged total  : {len(all_pkgs)} unique packages")

    # Optional: pin versions
    freeze_map = {}
    if args.freeze:
        freeze_map = get_pip_freeze()

    # Check for git-hosted packages
    git_pkgs = get_git_packages()

    # Write output
    with open(args.output, "w") as f:
        f.write("# ==============================================\n")
        f.write("# Auto-generated minimal requirements\n")
        f.write("# Static + Dynamic analysis merged\n")
        f.write("# ==============================================\n\n")

        # Regular packages
        regular = sorted(all_pkgs - set(git_pkgs.keys()))
        for pkg in regular:
            if args.freeze and pkg in freeze_map:
                f.write(f"{freeze_map[pkg]}\n")
            else:
                f.write(f"{pkg}\n")

        # Git-hosted packages
        git_in_deps = {k: v for k, v in git_pkgs.items() if k in all_pkgs}
        if git_in_deps:
            f.write("\n# ==============================================\n")
            f.write("# Git-hosted packages\n")
            f.write("# ==============================================\n")
            for name, spec in sorted(git_in_deps.items()):
                f.write(f"{spec}\n")

    print(f"\n✅ Written to: {args.output}")
    if git_in_deps:
        print(f"   (includes {len(git_in_deps)} git-hosted packages)")


if __name__ == "__main__":
    main()
