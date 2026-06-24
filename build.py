#!/usr/bin/env python3
"""
Build script for HonToAnki.

Usage:
    python build.py all          # Build all platforms
    python build.py windows      # Windows MSI + ZIP
    python build.py macos        # macOS PKG
    python build.py linux        # Linux deb + rpm
    python build.py portable     # Portable ZIPs for current platform
"""
import subprocess
import sys


def run(cmd, desc):
    print(f"\n=== {desc} ===")
    subprocess.run(cmd, check=True)


def build_platform(platform, package_args, fmt=None):
    cmd = ["briefcase", "create", platform]
    if fmt:
        cmd.append(fmt)
    run(cmd, f"Create {platform} {fmt or ''}")
    cmd = ["briefcase", "build", platform]
    if fmt:
        cmd.append(fmt)
    run(cmd, f"Build {platform} {fmt or ''}")
    for args in package_args:
        cmd = ["briefcase", "package", platform]
        if fmt:
            cmd.append(fmt)
        cmd.extend(args)
        run(cmd, f"Package {platform} {fmt or ''} ({args or 'default'})")


PLATFORM_MAP = {
    "win": "windows",
    "windows": "windows",
    "window": "windows",
    "mac": "macos",
    "macos": "macos",
    "osx": "macos",
    "linux": "linux",
}


def main():
    args = [a.lower() for a in sys.argv[1:]]
    if not args or "all" in args:
        build_platform("windows", [[], ["-p", "zip"]])
        build_platform("macos", [["-p", "pkg", "--adhoc-sign"]])
        build_platform("linux", [["-p", "deb"], ["-p", "rpm"]], fmt="system")
        return

    if "portable" in args:
        import platform
        system = platform.system()
        if system == "Windows":
            build_platform("windows", [["-p", "zip"]])
        elif system == "Darwin":
            build_platform("macos", [["-p", "pkg", "--adhoc-sign"]])
        else:
            build_platform("linux", [["-p", "deb"], ["-p", "rpm"]], fmt="system")
        return

    for a in args:
        plat = PLATFORM_MAP.get(a)
        if plat == "windows":
            build_platform("windows", [[], ["-p", "zip"]])
        elif plat == "macos":
            build_platform("macos", [["-p", "pkg", "--adhoc-sign"]])
        elif plat == "linux":
            build_platform("linux", [["-p", "deb"], ["-p", "rpm"]], fmt="system")

    if not any(a in PLATFORM_MAP for a in args):
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
